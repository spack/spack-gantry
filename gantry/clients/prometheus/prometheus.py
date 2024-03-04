import logging
import math

import aiohttp

from gantry.clients.prometheus import util
from gantry.clients.prometheus.job import PrometheusJobClient
from gantry.clients.prometheus.node import PrometheusNodeClient

logger = logging.getLogger(__name__)


class PrometheusClient:
    def __init__(self, base_url: str, auth_cookie: str = ""):
        # cookie will only be used if set
        if auth_cookie:
            self.cookies = {"_oauth2_proxy": auth_cookie}
        else:
            self.cookies = {}

        self.base_url = base_url

    async def query_single(self, query: str | dict, time: int) -> list:
        """Query Prometheus for a single value
        args:

            query: str or dict
                if str, the query string
                if dict, the metric and filters
                example:
                    "query": {
                        "metric": "metric_name",
                        "filters": {"filter1": "value1", "filter2": "value2"}
                    }
            time: int (unix timestamp)

        returns: dict with {label: value} format
        """

        query = util.process_query(query)
        url = f"{self.base_url}/query?query={query}&time={time}"
        return self.prettify_res(await self._query(url))

    async def query_range(self, query: str | dict, start: int, end: int) -> list:
        """Query Prometheus for a range of values

        args:
            query: see query_single
            start: int (unix timestamp)
            end: int (unix timestamp)

        returns: list of dicts with {label: value} format
        """

        query = util.process_query(query)
        # prometheus will only return this many frames
        max_resolution = 10_000
        # calculating the max step size to get the desired resolution
        step = math.ceil((end - start) / max_resolution)
        url = (
            f"{self.base_url}/query_range?"
            f"query={query}&"
            f"start={start}&"
            f"end={end}&"
            f"step={step}s"
        )
        return self.prettify_res(await self._query(url))

    async def _query(self, url: str) -> list:
        """Query Prometheus with a query string"""
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            # submit cookie with request
            async with session.get(url, cookies=self.cookies) as resp:
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    logger.error(
                        """Prometheus query failed with unexpected response.
                        The cookie may have expired."""
                    )
                    return {}

    def prettify_res(self, response: dict) -> list:
        """Process Prometheus response into a list of dicts with {label: value}"""
        result_type = response.get("data", {}).get("resultType")
        values_dict = {
            "matrix": "values",
            "vector": "value",
        }

        if result_type not in values_dict:
            logger.error(f"Prometheus response type {result_type} not supported")
            return []

        return [
            {"labels": result["metric"], "values": result[values_dict[result_type]]}
            for result in response["data"]["result"]
        ]

    @property
    def job(self):
        return PrometheusJobClient(self)

    @property
    def node(self):
        return PrometheusNodeClient(self)
