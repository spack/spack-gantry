# don't include retried builds in prediction bc of bias?

# - [ ] only allow upper bounds for now
# - [ ] weigh the most current build higher because of the retried jobs recursion thing
# - [ ] is there a need to set up some sort of cache?
# 	- [ ] like cache the calculation...hash the combo of parameters and store the prediction in a db table rather than doing calculation on the fly
# - store the current bounds static and make sure you don't go below? how would that work with the build size param...will it still exist?


import aiosqlite

MIN_TRAIN_SAMPLE = 4


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
        query = f"SELECT cpu_mean, cpu_max, mem_mean, mem_max FROM builds WHERE ref='develop' AND {' AND '.join(f'{param}=?' for param in combo)} ORDER BY end DESC LIMIT 5"
        async with db.execute(query, condition_values) as cursor:
            builds = await cursor.fetchall()
            if len(builds) >= MIN_TRAIN_SAMPLE:
                return builds

    return []


async def predict_resource_usage(db: aiosqlite.Connection, build: dict) -> dict:
    """
    Predict the resource usage of a build

    args:
        build: dict that must contain pkg name, pkg version, compiler, compiler version
    returns:
        dict of predicted resource usage: cpu_request, cpu_limit, mem_request, mem_limit. CPU in cores, mem in MB
    """

    sample = await sample(db, build)
    if not sample:
        return {
            "cpu_request": 1.0,
            "cpu_limit": None,
            "mem_request": 2000,
            "mem_limit": None,
        }
    
    # mapping of sample: [0] cpu_mean, [1] cpu_max, [2] mem_mean, [3] mem_max
    return {
        # averages the respective metric in the sample
        "cpu_request": sum([build[0] for build in sample]) / len(sample),
        "cpu_limit": None,
        # "cpu_limit": sum([build[1] for build in sample]) / len(sample),
        "mem_request": sum([build[2] for build in sample]) / len(sample),
        "mem_limit": None,
        # "mem_limit": sum([build[3] for build in sample]) / len(sample),
    }


async def handle_bulk(db: aiosqlite.Connection, builds: list) -> list:
    """
    Handles a bulk request of builds

    args:
        builds: list of dicts that must contain pkg name, pkg version, compiler, compiler version
    returns:
        list of dicts with predicted resource usage: cpu_request, cpu_limit, mem_request, mem_limit. CPU in cores, mem in MB
    """

    return [await predict_resource_usage(db, build) for build in builds]