# setup:
# 1. copy the latest gantry db from s3 to a directory, export it to DB_FILE
# 2. copy the file to a different path and set DB_FILE in a different terminal session

# choose how many jobs to predict and set JOBS_TO_PREDICT
# in the training db, run `delete from jobs order by id desc limit JOBS_TO_PREDICT;`
# to ensure that we aren't predicting from our training data
# then run the gantry web server `python -m gantry`

# run this script to simulate the prediction of the last JOBS_TO_PREDICT jobs
# the script will print the average of the memory and cpu ratios of the predictions

# litestream restore -o db s3://spack-gantry/db
# cp db test.db
# cp db train.db


# in a console session
# sqlite3 train.db
# delete from jobs order by id desc limit 8000;
# export DB_FILE=data/train.db
# python -m gantry

# in a different console session
# export DB_FILE=data/test.db
# python dev/simulate_predict.py

import asyncio
import json
import os
import time
from urllib.parse import quote

import aiohttp
import aiosqlite

JOBS_TO_PREDICT = 8000
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

    start_time = time.monotonic()
    async with session.get(f"{GANTRY_URL}/v1/allocation?spec={quote(spec)}") as resp:
        re = await resp.text()
        try:
            re = json.loads(re)
        except Exception:
            print(f"error: {re} for spec {spec}")
            exit()
        end_time = time.monotonic()

        # remove M from the end i.e 200M -> 200
        pred_mem_mean = int(re["variables"]["KUBERNETES_MEMORY_REQUEST"][:-1])
        pred_cpu_mean = (
            float(re["variables"]["KUBERNETES_CPU_REQUEST"][:-1]) / 1000
        )  # millicores
        pred_mem_max = int(re["variables"]["KUBERNETES_MEMORY_LIMIT"][:-1])
        pred_cpu_max = float(re["variables"]["KUBERNETES_CPU_LIMIT"][:-1]) / 1000
        mem_mean = j["mem_mean"] / 1_000_000  # bytes to MB
        cpu_mean = j["cpu_mean"]
        mem_max = j["mem_max"] / 1_000_000
        cpu_max = j["cpu_max"]

        ratios = {
            "mem_mean": (mem_mean / pred_mem_mean),
            "cpu_mean": (cpu_mean / pred_cpu_mean),
            "mem_max": (mem_max / pred_mem_max),
            "cpu_max": (cpu_max / pred_cpu_max),
            "time": round((end_time - start_time) * 1000, 2),
        }

        return ratios


async def main():
    jobs = await get_jobs()
    ratios = {"mem_mean": [], "cpu_mean": [], "mem_max": [], "cpu_max": [], "time": []}

    async with aiohttp.ClientSession() as session:
        for job in jobs:
            pred = await predict(job, session)
            ratios["mem_mean"].append(pred["mem_mean"])
            ratios["cpu_mean"].append(pred["cpu_mean"])
            ratios["mem_max"].append(pred["mem_max"])
            ratios["cpu_max"].append(pred["cpu_max"])
            ratios["time"].append(pred["time"])

    def avg(lst):
        return round(sum(lst) / len(lst), 4)

    print(f"ratio: mean mem usage {avg(ratios['mem_mean'])}")
    print(f"ratio: mean cpu usage {avg(ratios['cpu_mean'])}")
    print(f"ratio: max mem usage {avg(ratios['mem_max'])}")
    print(f"ratio: max cpu usage {avg(ratios['cpu_max'])}")
    # how many jobs went over the limit
    print(f"{len([x for x in ratios['mem_max'] if x > 1])} jobs killed")

    if os.environ.get("PROFILE") == "1":
        print("\n")
        print(f"mean time per prediction: {round(avg(ratios['time']), 2)}ms")
        print(f"min time per prediction: {min(ratios['time'])}ms")
        print(f"max time per prediction: {max(ratios['time'])}ms")
        print(f"total time: {round(sum(ratios['time'])/1000, 2)}s")


if __name__ == "__main__":
    asyncio.run(main())
