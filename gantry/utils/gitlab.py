import logging
import os

import aiohttp


class GitlabClient:
    def __init__(self):
        self.base_url = os.environ["GITLAB_URL"]
        self.headers = {"PRIVATE-TOKEN": os.environ["GITLAB_TOKEN"]}

    async def request(self, url: str, response_type: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    logging.error(f"Gitlab query failed with status {resp.status}")
                    return {}
                if response_type == "json":
                    return await resp.json()
                if response_type == "text":
                    return await resp.text()

    async def job_log(self, id: int) -> str:
        url = f"{self.base_url}/jobs/{id}/trace"
        return await self.request(url, "text")
