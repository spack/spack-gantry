import urllib.parse

import aiohttp


class GitlabClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {"PRIVATE-TOKEN": api_token}

    async def _request(self, method: str, url: str, response_type: str) -> dict | str:
        """
        Helper for requests to the Gitlab API.

        args:
            method: HTTP method (GET, POST)
            url: the url to request
            response_type: the type of response to expect (json, text by default)

        returns: the response from Gitlab in the specified format
        """

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.request(method, url, headers=self.headers) as resp:
                if response_type == "json":
                    return await resp.json()
                return await resp.text()

    async def job_log(self, gl_id: int) -> str:
        """Given a job id, returns the log from that job"""

        url = f"{self.base_url}/jobs/{gl_id}/trace"
        return await self._request("get", url, "text")

    async def start_pipeline(self, ref: str) -> dict:
        """Given a ref, starts a pipeline"""
        url = f"{self.base_url}/pipeline?ref={urllib.parse.quote(ref)}"
        return await self._request("POST", url, "json")
