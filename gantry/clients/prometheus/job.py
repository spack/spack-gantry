import json

import aiosqlite

from gantry.clients.prometheus import util
from gantry.util.spec import spec_variants


class PrometheusJobClient:
    def __init__(self, client):
        self.client = client

    async def get_annotations(self, gl_id: int, time: float) -> dict:
        """
        args:
            gl_id: gitlab job id
            time: when to query (unix timestamp)
        returns: dict of annotations
        """

        res = await self.client.query_single(
            query={
                "metric": "kube_pod_annotations",
                "filters": {"annotation_gitlab_ci_job_id": gl_id},
            },
            time=time,
        )

        if not res:
            raise util.IncompleteData("annotation data is missing")

        annotations = res[0]["labels"]

        try:
            return {
                "pod": annotations["pod"],
                # if build jobs is not set, defaults to 16 due to spack config
                "build_jobs": annotations.get(
                    "annotation_metrics_spack_job_build_jobs", 16
                ),
                "arch": annotations["annotation_metrics_spack_job_spec_arch"],
                "pkg_name": annotations["annotation_metrics_spack_job_spec_pkg_name"],
                "pkg_version": annotations[
                    "annotation_metrics_spack_job_spec_pkg_version"
                ],
                "pkg_variants": json.dumps(
                    spec_variants(
                        annotations["annotation_metrics_spack_job_spec_variants"]
                    )
                ),
                "compiler_name": annotations[
                    "annotation_metrics_spack_job_spec_compiler_name"
                ],
                "compiler_version": annotations[
                    "annotation_metrics_spack_job_spec_compiler_version"
                ],
                "stack": annotations["annotation_metrics_spack_ci_stack_name"],
            }
        except KeyError as e:
            # if any of the annotations are missing, raise an error
            raise util.IncompleteData(f"missing annotation: {e}")

    async def get_resources(self, pod: str, time: float) -> tuple[dict, str]:
        """
        args:
            pod: pod name
            time: when to query (unix timestamp)
        returns: dict of resources and node hostname
        """

        requests = util.process_resources(
            await self.client.query_single(
                query={
                    "metric": "kube_pod_container_resource_requests",
                    "filters": {"container": "build", "pod": pod},
                },
                time=time,
            )
        )

        limits_res = await self.client.query_single(
            query={
                "metric": "kube_pod_container_resource_limits",
                "filters": {"container": "build", "pod": pod},
            },
            time=time,
        )

        if not limits_res:
            raise util.IncompleteData("missing limits")

        # instead of needing to fetch the node where the pod ran from kube_pod_info
        # we can grab it from kube_pod_container_resource_limits
        # weirdly, it's not available in kube_pod_labels or annotations
        # https://github.com/kubernetes/kube-state-metrics/issues/1148
        try:
            node = limits_res[0]["labels"]["node"]
        except KeyError:
            raise util.IncompleteData("missing node label")
        limits = util.process_resources(limits_res)

        return (
            {
                "cpu_request": requests["cpu"]["value"],
                "mem_request": requests["memory"]["value"],
                "cpu_limit": limits.get("cpu", {}).get("value"),
                "mem_limit": limits["memory"]["value"],
            },
            node,
        )

    async def get_usage(self, pod: str, start: float, end: float) -> dict:
        """
        Gets resource usage attributes for a job.

        args:
            pod: pod name
            start: start time (unix timestamp)
            end: end time (unix timestamp)
        returns: dict of usage stats
        """

        mem_usage = util.process_usage(
            await self.client.query_range(
                query={
                    "metric": "container_memory_working_set_bytes",
                    "filters": {"container": "build", "pod": pod},
                },
                start=start,
                end=end,
            )
        )

        cpu_usage = util.process_usage(
            await self.client.query_range(
                query=(
                    f"rate(container_cpu_usage_seconds_total{{"
                    f"pod='{pod}', container='build'}}[90s])"
                ),
                start=start,
                end=end,
            )
        )

        return {
            "cpu_mean": cpu_usage["mean"],
            "cpu_median": cpu_usage["median"],
            "cpu_max": cpu_usage["max"],
            "cpu_min": cpu_usage["min"],
            "cpu_stddev": cpu_usage["stddev"],
            "mem_mean": mem_usage["mean"],
            "mem_median": mem_usage["median"],
            "mem_max": mem_usage["max"],
            "mem_min": mem_usage["min"],
            "mem_stddev": mem_usage["stddev"],
        }

    async def get_costs(
        self,
        db: aiosqlite.Connection,
        resources: dict,
        usage: dict,
        start: float,
        end: float,
        node_id: int,
    ) -> dict:
        """
        Calculates the costs associated with a job.

        Objectives:
            - we want to measure the cost of a job's submission and execution
            - measure efficiency of resource usage to discourage wasted cycles

        The cost should be independent of other activity on the node in order
        to be comparable against other jobs.

        To normalize the cost of resources within instance types, we calculate
        the cost of each CPU and memory unit in the node during the lifetime
        of the job.

        Rather than using real usage as a factor in the cost, we use the requests,
        as they block other jobs from using resources. In this case, jobs will be
        incentivized to make lower requests, while also factoring in the runtime.

        To account for instances where jobs do not use their requested resources (+/-),
        we compute a penalty factor that can be used to understand the cost imposed
        on the rest of the node, or jobs that could have been scheduled on the machine.

        Job cost and the penalties are stored separately for each resource to allow for
        flexibility. When analyzing these costs, instance type should be factored in,
        as the cost per job is influence by the cost per resource, which will vary.

        args:
            db: a database connection
            resources: job requests and limits
            usage: job memory and cpu usage
            start: job start time
            end: job end time
            node_id: the node that the job ran on

        returns:
            dict of: cpu_cost, mem_cost, cpu_penalty, mem_penalty
        """
        costs = {}
        async with db.execute(
            """
                select capacity_type, instance_type, zone, cores, mem
                from nodes where id = ?
            """,
            (node_id,),
        ) as cursor:
            node = await cursor.fetchone()

        if not node:
            # this is a temporary condition that will happen during the transition
            # to collecting
            raise util.IncompleteData(
                f"node instance metadata is missing from db. node={node_id}"
            )

        capacity_type, instance_type, zone, cores, mem = node

        # spot instance prices can change, so we avg the cost over the job's runtime
        instance_costs = await self.client.query_range(
            query={
                "metric": "karpenter_cloudprovider_instance_type_offering_price_estimate",  # noqa: E501
                "filters": {
                    "capacity_type": capacity_type,
                    "instance_type": instance_type,
                    "zone": zone,
                },
            },
            start=start,
            end=end,
        )

        if not instance_costs:
            raise util.IncompleteData(f"node cost is missing. node={node_id}")

        instance_costs = [float(value) for _, value in instance_costs[0]["values"]]
        # average hourly cost of the instance over the job's lifetime
        instance_cost = sum(instance_costs) / len(instance_costs)
        # compute cost relative to duration of the job (in seconds)
        node_cost = instance_cost * ((end - start) / 60 / 60)

        # we assume that the cost of the node is split evenly between cpu and memory
        # cost of each CPU in the node during the lifetime of the job
        cost_per_cpu = (node_cost * 0.5) / cores
        # cost of each unit of memory (byte)
        cost_per_mem = (node_cost * 0.5) / mem

        # base cost of a job is the resources it consumed (usage)
        costs["cpu_cost"] = usage["cpu_mean"] * cost_per_cpu
        costs["mem_cost"] = usage["mem_mean"] * cost_per_mem

        # penalty factors are meant to capture misallocation, or the
        # opportunity cost of the job's behavior on the cluster/node
        # underallocation delays scheduling of other jobs, increasing pipeline duration
        # overallocation interferes with the work of other jobs and crowds the node
        # the penalty is the absolute difference between the job's usage and request
        costs["cpu_penalty"] = (
            abs(usage["cpu_mean"] - resources["cpu_request"]) * cost_per_cpu
        )
        costs["mem_penalty"] = (
            abs(usage["mem_mean"] - resources["mem_request"]) * cost_per_mem
        )

        return costs
