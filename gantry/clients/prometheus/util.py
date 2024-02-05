import math
import statistics
import urllib.parse


class IncompleteData(Exception):
    pass


def process_query(query: dict | str) -> str:
    """
    Processes query into a string that can be used in a URL.
    See query_single in prometheus.py for more details on args.
    """
    if isinstance(query, dict):
        query = query_to_str(**query)
    elif not isinstance(query, str):
        raise ValueError("query must be a string or dict")

    return urllib.parse.quote(query)


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
