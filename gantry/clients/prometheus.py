import json
import logging
import math
import statistics
import urllib.parse

import aiohttp

from gantry.util.spec import spec_variants


class IncompleteData(Exception):
    pass


class PrometheusClient:
    def __init__(self, base_url: str, auth_cookie: str = ""):
        # cookie will only be used if set
        if auth_cookie:
            self.cookies = {"_oauth2_proxy": auth_cookie}
        else:
            self.cookies = {}

        self.base_url = base_url

    async def query(self, type: str, **kwargs) -> dict:
        """
        type: "range" or "single"

        for range queries: set `start` and `end` (unix timestamps)
        for single queries: set `time` (unix timestamp)

        for custom queries: set `custom_query` (string)

        for metric queries: set `query` (dict)
            example:
                "query": {
                    "metric": "metric_name",
                    "filters": {"filter1": "value1", "filter2": "value2"}
                }
        """

        # validate that one of query or custom_query is set, but not both or neither
        if not kwargs.get("query") and not kwargs.get("custom_query"):
            raise ValueError("query or custom_query must be set")
        if kwargs.get("query") and kwargs.get("custom_query"):
            raise ValueError("query and custom_query cannot both be set")

        query_str = urllib.parse.quote(
            kwargs["custom_query"]
            if kwargs.get("custom_query")
            else query_to_str(**kwargs["query"])
        )

        if type == "range":
            # prometheus will only return this many frames
            max_resolution = 10_000
            # calculating the max step size to get the desired resolution
            step = math.ceil((kwargs["end"] - kwargs["start"]) / max_resolution)
            url = (
                f"{self.base_url}/query_range?"
                f"query={query_str}&"
                f"start={kwargs['start']}&"
                f"end={kwargs['end']}&"
                f"step={step}s"
            )
            return await self._query(url)
        elif type == "single":
            url = f"{self.base_url}/query?query={query_str}&time={kwargs['time']}"
            return await self._query(url)

    async def _query(self, url: str) -> dict:
        """Query Prometheus with a query string"""
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            # submit cookie with request
            async with session.get(url, cookies=self.cookies) as resp:
                try:
                    return self.prettify_res(await resp.json())
                except aiohttp.ContentTypeError:
                    logging.error(
                        """Prometheus query failed with unexpected response.
                        The cookie may have expired."""
                    )
                    return {}

    def prettify_res(self, response: dict) -> dict:
        """Process Prometheus response into an arrray of dicts with {label: value}"""
        result_type = response.get("data", {}).get("resultType")
        values_dict = {
            "matrix": "values",
            "vector": "value",
        }

        if result_type not in values_dict:
            logging.error(f"Prometheus response type {result_type} not supported")
            return {}

        return [
            {"labels": result["metric"], "values": result[values_dict[result_type]]}
            for result in response["data"]["result"]
        ]

    async def get_job_annotations(self, job_id: int, time: float) -> dict:
        """
        args:
            job_id: job id
            time: when to query (unix timestamp)
        returns: dict of annotations
        """

        res = await self.query(
            type="single",
            query={
                "metric": "kube_pod_annotations",
                "filters": {"annotation_gitlab_ci_job_id": job_id},
            },
            time=time,
        )

        if not res:
            raise IncompleteData("annotation data is missing")

        annotations = res[0]["labels"]

        return {
            "pod": annotations["pod"],
            # if build jobs is not set, defaults to 16 due to spack config
            "build_jobs": annotations.get(
                "annotation_metrics_spack_job_build_jobs", 16
            ),
            "arch": annotations["annotation_metrics_spack_job_spec_arch"],
            "pkg_name": annotations["annotation_metrics_spack_job_spec_pkg_name"],
            "pkg_version": annotations["annotation_metrics_spack_job_spec_pkg_version"],
            "pkg_variants": json.dumps(
                spec_variants(annotations["annotation_metrics_spack_job_spec_variants"])
            ),
            "compiler_name": annotations[
                "annotation_metrics_spack_job_spec_compiler_name"
            ],
            "compiler_version": annotations[
                "annotation_metrics_spack_job_spec_compiler_version"
            ],
            "stack": annotations["annotation_metrics_spack_ci_stack_name"],
        }

    async def get_job_resources(self, pod: str, time: float) -> tuple[dict, str]:
        """
        args:
            job_id: job id
            pod: pod name
            time: when to query (unix timestamp)
        returns: dict of resources and node hostname
        """

        requests = process_resources(
            await self.query(
                type="single",
                query={
                    "metric": "kube_pod_container_resource_requests",
                    "filters": {"container": "build", "pod": pod},
                },
                time=time,
            )
        )

        limits_res = await self.query(
            type="single",
            query={
                "metric": "kube_pod_container_resource_limits",
                "filters": {"container": "build", "pod": pod},
            },
            time=time,
        )

        if not limits_res:
            raise IncompleteData("missing limits")

        # instead of needing to fetch the node where the pod ran from kube_pod_info
        # we can grab it from kube_pod_container_resource_limits
        # weirdly, it's not available in kube_pod_labels or annotations
        # https://github.com/kubernetes/kube-state-metrics/issues/1148
        node = limits_res[0]["labels"]["node"]
        limits = process_resources(limits_res)

        return (
            {
                "cpu_request": requests["cpu"]["value"],
                "mem_request": requests["memory"]["value"],
                "cpu_limit": limits.get("cpu", {}).get("value"),
                "mem_limit": limits["memory"]["value"],
            },
            node,
        )

    async def get_job_usage(self, pod: str, start: float, end: float) -> dict:
        """
        Gets resource usage attributes for a job.

        args:
            pod: pod name
            start: start time (unix timestamp)
            end: end time (unix timestamp)
        returns: dict of usage stats
        """

        mem_usage = process_usage(
            await self.query(
                type="range",
                query={
                    "metric": "container_memory_working_set_bytes",
                    "filters": {"container": "build", "pod": pod},
                },
                start=start,
                end=end,
            )
        )

        cpu_usage = process_usage(
            await self.query(
                type="range",
                custom_query=(
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

    async def get_node_uuid(self, hostname: str, time: float) -> dict:
        """
        args:
            hostname: node hostname
            time: time to query (unix timestamp)
        returns: dict of node info (UUID as of now)
        """

        res = await self.query(
            type="single",
            query={
                "metric": "kube_node_info",
                "filters": {"node": hostname},
            },
            time=time,
        )

        if not res:
            raise IncompleteData(f"node info is missing. hostname={hostname}")

        return res[0]["labels"]["system_uuid"]

    async def get_node_labels(self, hostname: str, time: float) -> dict:
        """
        args:
            hostname: node hostname
            time: time to query (unix timestamp)
        returns: dict of node labels
        """

        res = await self.query(
            type="single",
            query={
                "metric": "kube_node_labels",
                "filters": {"node": hostname},
            },
            time=time,
        )

        if not res:
            raise IncompleteData(f"node labels are missing. hostname={hostname}")

        labels = res[0]["labels"]

        return {
            "cores": float(labels["label_karpenter_k8s_aws_instance_cpu"]),
            "mem": float(labels["label_karpenter_k8s_aws_instance_memory"]),
            "arch": labels["label_kubernetes_io_arch"],
            "os": labels["label_kubernetes_io_os"],
            "instance_type": labels["label_node_kubernetes_io_instance_type"],
        }


def query_to_str(metric: str, filters: dict) -> str:
    """
    In: "metric", {key1: value1, key2: value2}
    Out: "metric{key1="value1", key2="value2"}"
    """
    filters_str = ", ".join([f'{key}="{value}"' for key, value in filters.items()])
    return f"{metric}{{{filters_str}}}"


def process_resources(res: dict) -> dict:
    """
    Processes the resource limits and requests from a Prometheus response into
    readable format.

    args:
        res: Prometheus response

    returns: dict with {resource: {unit: value}} format
    """

    if not res:
        raise IncompleteData("resource data is missing")

    processed = {}
    for item in res:
        # duplicates are ignored by overwriting the previous entry
        processed[item["labels"]["resource"]] = {
            "unit": item["labels"]["unit"],
            "value": float(item["values"][1]),
        }

    return processed


def process_usage(res: dict) -> dict:
    """
    Processes the usage data from a Prometheus response into readable format.
    This could either be CPU usage or memory usage.

    args:
        res: Prometheus response

    returns: dict with {statistic: value} format
    """

    if not res:
        # sometimes prometheus reports no data for a job if the time range is too small
        raise IncompleteData("usage data is missing")

    usage = [float(value) for timestamp, value in res[0]["values"]]

    sum_stats = {
        "mean": statistics.fmean(usage),
        # pstdev because we have the whole population
        "stddev": statistics.pstdev(usage),
        "max": max(usage),
        "min": min(usage),
        "median": statistics.median(usage),
    }

    if (
        sum_stats["stddev"] == 0
        or sum_stats["mean"] == 0
        or math.isnan(sum_stats["stddev"])
    ):
        raise IncompleteData("usage data is invalid")

    return sum_stats
