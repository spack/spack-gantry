import json

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
                "retry_count": int(
                    annotations.get("annotation_metrics_spack_job_retry_count", 0)
                ),
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

    async def is_oom(self, pod: str, start: float, end: float) -> bool:
        """checks if a job was OOM killed"""
        # TODO this does not work
        oom_status = await self.client.query_range(
            query={
                "metric": "kube_pod_container_status_last_terminated_reason",
                "filters": {"container": "build", "pod": pod, "reason": "OOMKilled"},
            },
            start=start,
            end=end + (10 * 60),  # 10 minute buffer, handle where there is no data...
        )

        return bool(oom_status)
