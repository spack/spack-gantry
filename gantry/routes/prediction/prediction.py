import logging

import aiosqlite

from gantry.routes.prediction.current_mapping import pkg_mappings

MIN_TRAIN_SAMPLE = 4
DEFAULT_CPU_REQUEST = 1.0
DEFAULT_MEM_REQUEST = 2000 * 1_000_000  # 2GB in bytes

CORES_TO_MILLICORES = 1000
BYTES_TO_MEGABYTES = 1 / 1_000_000


def preprocess_pred(prediction, pkg_name):
    """
    Main goal of this function is to ensure that our
    prediction is not lower than the current allocation
    for that package. This restriction will likely be
    removed in the future as we understand the effectiveness
    of the prediction model.
    """

    cur_alloc = pkg_mappings.get(pkg_name)

    if cur_alloc:
        prediction["variables"]["KUBERNETES_CPU_REQUEST"] = max(
            prediction["variables"]["KUBERNETES_CPU_REQUEST"], cur_alloc["cpu_request"]
        )
        prediction["variables"]["KUBERNETES_MEMORY_REQUEST"] = max(
            prediction["variables"]["KUBERNETES_MEMORY_REQUEST"],
            cur_alloc["mem_request"],
        )

    # put into k8s friendly format
    prediction["variables"]["KUBERNETES_CPU_REQUEST"] = (
        str(
            int(prediction["variables"]["KUBERNETES_CPU_REQUEST"] * CORES_TO_MILLICORES)
        )
        + "m"
    )
    prediction["variables"]["KUBERNETES_MEMORY_REQUEST"] = (
        str(
            int(
                prediction["variables"]["KUBERNETES_MEMORY_REQUEST"]
                * BYTES_TO_MEGABYTES
            )
        )
        + "M"
    )

    return prediction


async def get_sample(db: aiosqlite.Connection, build: dict) -> list:
    """
    Selects a sample of builds to use for prediction

    args:
        build: dict that must contain pkg name, pkg version, compiler, compiler version
    returns:
        list of lists with cpu_mean, cpu_max, mem_mean, mem_max
    """

    flat_build = {
        "pkg_name": build["package"]["name"],
        "pkg_version": build["package"]["version"],
        "compiler_name": build["compiler"]["name"],
        "compiler_version": build["compiler"]["version"],
    }

    param_combos = [
        ("pkg_name", "pkg_version", "compiler_name", "compiler_version"),
        ("pkg_name", "compiler_name", "compiler_version"),
        ("pkg_name", "pkg_version", "compiler_name"),
        ("pkg_name", "compiler_name"),
        ("pkg_name", "pkg_version"),
        ("pkg_name",),
    ]

    for combo in param_combos:
        condition_values = [flat_build[param] for param in combo]
        query = f"""
        SELECT cpu_mean, cpu_max, mem_mean, mem_max FROM jobs WHERE ref='develop'
        AND {' AND '.join(f'{param}=?' for param in combo)}
        ORDER BY end DESC LIMIT {MIN_TRAIN_SAMPLE + 1}
        """
        async with db.execute(query, condition_values) as cursor:
            sample = await cursor.fetchall()
            if len(sample) >= MIN_TRAIN_SAMPLE:
                return sample

    return []


async def predict_single(db: aiosqlite.Connection, build: dict) -> dict:
    """
    Predict the resource usage of a build

    args:
        build: dict that must contain pkg name, pkg version, compiler, compiler version
    returns:
        dict of predicted resource usage: cpu_request, mem_request
        CPU in millicore, mem in MB
    """

    sample = await get_sample(db, build)
    if not sample:
        vars = {
            "KUBERNETES_CPU_REQUEST": DEFAULT_CPU_REQUEST,
            "KUBERNETES_MEMORY_REQUEST": DEFAULT_MEM_REQUEST,
        }
    else:
        # mapping of sample: [0] cpu_mean, [1] cpu_max, [2] mem_mean, [3] mem_max
        vars = {
            # averages the respective metric in the sample
            "KUBERNETES_CPU_REQUEST": sum([build[0] for build in sample]) / len(sample),
            "KUBERNETES_MEMORY_REQUEST": (
                sum([build[2] for build in sample]) / len(sample)
            ),
        }

    pred = {
        "hash": build["hash"],
        "variables": vars,
    }

    if pred["variables"]["KUBERNETES_CPU_REQUEST"] < 0.25:
        logging.warning(f"Warning: CPU request for {build['hash']} is below 0.25 cores")
    if pred["variables"]["KUBERNETES_MEMORY_REQUEST"] < 10000000:
        logging.warning(f"Warning: Memory request for {build['hash']} is below 10MB")

    return preprocess_pred(pred, build["package"]["name"])


async def predict_bulk(db: aiosqlite.Connection, builds: list) -> list:
    """
    Handles a bulk request of builds

    args:
        builds: list of dicts (see predict_single)
    returns: see predict_single)
    """

    return [await predict_single(db, build) for build in builds]
