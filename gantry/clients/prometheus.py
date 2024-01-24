import logging
import math
import statistics
import urllib.parse

import aiohttp


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


def query_to_str(metric: str, filters: dict) -> str:
    """
    In: "metric", {key1: value1, key2: value2}
    Out: "metric{key1="value1", key2="value2"}"
    """
    filters_str = ", ".join([f'{key}="{value}"' for key, value in filters.items()])
    return f"{metric}{{{filters_str}}}"


def process_resources(res: dict, job_id: int) -> dict:
    """
    Processes the resource limits and requests from a Prometheus response into
    readable format.

    args:
        res: Prometheus response
        job_id: job id for error logging

    returns: dict with {resource: {unit: value}} format
    """

    if not res:
        raise IncompleteData(f"resource data is missing for job {job_id}")

    processed = {}
    for item in res:
        # duplicates are ignored by overwriting the previous entry
        processed[item["labels"]["resource"]] = {
            "unit": item["labels"]["unit"],
            "value": float(item["values"][1]),
        }

    return processed


def process_usage(res: dict, job_id: int) -> dict:
    """
    Processes the usage data from a Prometheus response into readable format.
    This could either be CPU usage or memory usage.

    args:
        res: Prometheus response
        job_id: job id for error logging

    returns: dict with {statistic: value} format
    """

    if not res:
        # sometimes prometheus reports no data for a job if the time range is too small
        raise IncompleteData(f"usage data is missing for job {job_id}")

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
        raise IncompleteData(f"usage data is invalid for job {job_id}")

    return sum_stats
