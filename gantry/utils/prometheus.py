import logging
import math
import os
import urllib.parse

import aiohttp


class PrometheusClient:
    # TODO error handling for unexpected data
    # todo retry mechanism for failed requests?

    def __init__(self):
        self.base_url = os.environ["PROMETHEUS_URL"]
        self.cookies = {"_oauth2_proxy": os.environ["PROMETHEUS_COOKIE"]}

    async def query(self, type: str, **kwargs) -> dict:
        # TODO add validation for kwargs and comments
        query_str = (
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
        async with aiohttp.ClientSession() as session:
            # submit cookie with request
            async with session.get(url, cookies=self.cookies) as resp:
                if resp.status != 200:
                    logging.error(f"Prometheus query failed with status {resp.status}")
                    return {}
                try:
                    return self.process_response(await resp.json())
                except aiohttp.ContentTypeError:
                    logging.error(
                        """Prometheus query failed with unexpected response.
                        The cookie may have expired."""
                    )
                    return {}

    def process_response(self, response: dict) -> dict:
        """Process Prometheus response into a more usable format"""
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
    # TODO add a test for this
    # expected output: metric{key1="val1", key2="val2"}
    filters_str = ", ".join([f'{key}="{value}"' for key, value in filters.items()])
    return urllib.parse.quote(f"{metric}{{{filters_str}}}")
