import aiohttp


class GitlabClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {"PRIVATE-TOKEN": api_token}

    async def _request(self, url: str, response_type: str) -> dict | str:
        """
        Helper for requests to the Gitlab API.

        args:
            url: the url to request
            response_type: the type of response to expect (json or text)

        returns: the response from Gitlab in the specified format
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if response_type == "json":
                    return await resp.json()
                if response_type == "text":
                    return await resp.text()

    async def job_log(self, gl_id: int) -> str:
        """Given a job id, returns the log from that job"""

        url = f"{self.base_url}/jobs/{gl_id}/trace"
        return await self._request(url, "text")
