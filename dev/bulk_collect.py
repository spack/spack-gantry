# simulates a bulk sending of webhooks to gantry

import asyncio
import os
from datetime import datetime

import aiohttp

# how many jobs to retrieve from gitlab (100 per page)
NUM_GL_PAGES = 3
GANTRY_URL = "http://localhost:8080"


async def get_gitlab_jobs():
    headers = {"PRIVATE-TOKEN": os.environ["GITLAB_API_TOKEN"]}
    responses = []

    for i in range(1, NUM_GL_PAGES + 1):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://gitlab.spack.io/api/v4/projects/2/jobs?page={i}&per_page=100",
                headers=headers,
            ) as response:
                resp = await response.json()
                responses += resp
    return responses


async def webhook(job):
    headers = {
        "X-Gitlab-Event": "Job Hook",
        "X-Gitlab-Token": os.environ["GITLAB_WEBHOOK_TOKEN"],
    }
    job["build_status"] = job["status"]
    job["build_name"] = job["name"]
    job["build_id"] = job["id"]
    if job["started_at"] is None or job["finished_at"] is None:
        return
    else:
        # weirdly gitlab job api datetime format is different from the webhook format
        dt = datetime.strptime(job["started_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        job["build_started_at"] = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        dt = datetime.strptime(job["finished_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        job["build_finished_at"] = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GANTRY_URL}/v1/collect", headers=headers, json=job
        ) as response:
            if response.status != 200:
                print(f"failed to send job {job['id']} to gantry: {response.status}")


async def main():
    print("retrieving list of jobs...")
    jobs = await get_gitlab_jobs()
    for job in jobs:
        await webhook(job)


if __name__ == "__main__":
    asyncio.run(main())
