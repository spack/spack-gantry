# - [ ] only allow upper bounds for now
# - store the current bounds static and make sure you don't go below? how would that work with the build size param...will it still exist?
# should we match kubernetes units? do we want to make it generic? in the prediction api MR


import aiosqlite

MIN_TRAIN_SAMPLE = 4
DEFAULT_CPU_REQUEST = 1.0
DEFAULT_MEM_REQUEST = 2000


async def select_sample(db: aiosqlite.Connection, build: dict) -> list:
    """
    Selects a sample of builds to use for prediction

    args:
        build: dict that must contain pkg name, pkg version, compiler, compiler version
    returns:
        list of lists with cpu_mean, cpu_max, mem_mean, mem_max
    """

    param_combos = [
        ("pkg_name", "pkg_version", "compiler_name", "compiler_version"),
        ("pkg_name", "compiler_name", "compiler_version"),
        ("pkg_name", "pkg_version", "compiler_name"),
        ("pkg_name", "compiler_name"),
        ("pkg_name", "pkg_version"),
        ("pkg_name"),
    ]

    for combo in param_combos:
        condition_values = [build[param] for param in combo]
        query = f"SELECT cpu_mean, cpu_max, mem_mean, mem_max FROM builds WHERE ref='develop' AND {' AND '.join(f'{param}=?' for param in combo)} ORDER BY end DESC LIMIT {MIN_TRAIN_SAMPLE + 1}"
        async with db.execute(query, condition_values) as cursor:
            builds = await cursor.fetchall()
            if len(builds) >= MIN_TRAIN_SAMPLE:
                return builds

    return []


async def predict_single(db: aiosqlite.Connection, build: dict) -> dict:
    """
    Predict the resource usage of a build

    args:
        build: dict that must contain pkg name, pkg version, compiler, compiler version
    returns:
        dict of predicted resource usage: cpu_request, cpu_limit, mem_request, mem_limit. CPU in cores, mem in MB
    """

    sample = await sample(db, build)
    if not sample:
        vars = {
            "cpu_request": DEFAULT_CPU_REQUEST,
            "mem_request": DEFAULT_MEM_REQUEST,
        }
    else:
        # mapping of sample: [0] cpu_mean, [1] cpu_max, [2] mem_mean, [3] mem_max
        vars = {
            # averages the respective metric in the sample
            "cpu_request": sum([build[0] for build in sample]) / len(sample),
            "mem_request": sum([build[2] for build in sample]) / len(sample),
        }

    return {
        "hash": build["hash"],
        "variables": vars,
    }


async def predict_bulk(db: aiosqlite.Connection, builds: list) -> list:
    """
    Handles a bulk request of builds

    args:
        builds: list of dicts that must contain pkg name, pkg version, compiler, compiler version
    returns:
        list of dicts with predicted resource usage: cpu_request, cpu_limit, mem_request, mem_limit. CPU in cores, mem in MB
    """

    return [await predict_single(db, build) for build in builds]