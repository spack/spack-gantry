# setup:
# 1. copy the latest gantry db from s3 to a directory, export it to DB_FILE
# 2. copy the file to a different path and set DB_FILE in a different terminal session

# choose how many jobs to predict and set JOBS_TO_PREDICT
# in db #2, run `delete from jobs order by id desc limit JOBS_TO_PREDICT;`
# to ensure that we aren't predicting from our training data
# then run the gantry web server `python -m gantry`

# run this script to simulate the prediction of the last JOBS_TO_PREDICT jobs
# the script will print the average of the memory and cpu ratios of the predictions

import asyncio
import json
import os
from urllib.parse import quote

import aiohttp
import aiosqlite

JOBS_TO_PREDICT = 4000
GANTRY_URL = "http://localhost:8080"


def dict_to_spec(variants: dict) -> str:
    """Given a dict in name: value format, return a spec's concrete variants string."""
    spec_parts = []

    for name, value in variants.items():
        if isinstance(value, bool):
            # convert True/False to +/~ notation
            if value:
                spec_parts.append(f"+{name}")
            else:
                spec_parts.append(f"~{name}")
        elif isinstance(value, list):
            # join lists with commas
            spec_parts.append(f"{name}={','.join(value)}")
        else:
            # add name=value pairs
            spec_parts.append(f"{name}={value}")

    # join all parts into a single string with no space between `+` or `~` prefixes
    return " ".join(spec_parts).replace(" +", "+").replace(" ~", "~")


async def get_jobs():
    db = await aiosqlite.connect(os.environ["DB_FILE"])

    async with db.execute(
        f"select * from jobs order by id desc limit {JOBS_TO_PREDICT}"
    ) as cursor:
        jobs = await cursor.fetchall()

    await db.close()
    return jobs


async def predict(job, session):
    # can delete from here if you don't need
    j = {
        "id": job[0],
        "pod": job[1],
        "node": job[2],
        "start": job[3],
        "end": job[4],
        "gitlab_id": job[5],
        "job_status": job[6],
        "ref": job[7],
        "pkg_name": job[8],
        "pkg_version": job[9],
        "pkg_variants": job[10],
        "compiler_name": job[11],
        "compiler_version": job[12],
        "arch": job[13],
        "stack": job[14],
        "build_jobs": job[15],
        "cpu_request": job[16],
        "cpu_limit": job[17],
        "cpu_mean": job[18],
        "cpu_median": job[19],
        "cpu_max": job[20],
        "cpu_min": job[21],
        "cpu_stddev": job[22],
        "mem_request": job[23],
        "mem_limit": job[24],
        "mem_mean": job[25],
        "mem_median": job[26],
        "mem_max": job[27],
        "mem_min": job[28],
        "mem_stddev": job[29],
    }

    # json variants to spec format that gantry understands
    var = dict_to_spec(json.loads(j["pkg_variants"]))

    spec = (
        f"{j['pkg_name']}@{j['pkg_version']} {var}%{j['compiler_name']}"
        f"@{j['compiler_version']}"
    )

    async with session.get(f"{GANTRY_URL}/v1/allocation?spec={quote(spec)}") as resp:
        re = await resp.text()
        try:
            re = json.loads(re)
        except Exception:
            print(f"error: {re} for spec {spec}")
            exit()

        mem_prediction = re["variables"]["KUBERNETES_MEMORY_REQUEST"]
        # remove M from the end i.e 200M -> 200
        mem_prediction = int(mem_prediction[:-1])
        cpu_prediction = float(re["variables"]["KUBERNETES_CPU_REQUEST"])

        mem_usage = j["mem_mean"] / 1_000_000  # bytes to MB

        mem_ratio = (mem_usage) / mem_prediction
        cpu_ratio = j["cpu_mean"] / cpu_prediction

        return mem_ratio, cpu_ratio


async def main():
    jobs = await get_jobs()
    mem_preds = []
    cpu_preds = []
    async with aiohttp.ClientSession() as session:
        for job in jobs:
            pred = await predict(job, session)
            mem_preds.append(pred[0])
            cpu_preds.append(pred[1])

    print(f"average memory ratio: {sum(mem_preds)/len(mem_preds)}")
    print(f"average cpu ratio: {sum(cpu_preds)/len(cpu_preds)}")


if __name__ == "__main__":
    asyncio.run(main())
