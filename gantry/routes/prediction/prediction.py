import asyncio
import logging

# TODO clean all this up check obsidian notes to make sure everything's implemented

import aiosqlite

from gantry.routes.prediction.current_mapping import pkg_mappings
from gantry.util import k8s, spec

IDEAL_SAMPLE = 4
DEFAULT_CPU_REQUEST = 1.0
DEFAULT_MEM_REQUEST = 2000 * 1_000_000  # 2GB in bytes


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
    predictions = {}
    if not sample:
        predictions = {
            "cpu_request": DEFAULT_CPU_REQUEST,
            "mem_request": DEFAULT_MEM_REQUEST,
        }
    else:
        # mapping of sample: [1] cpu_mean, [2] cpu_max, [3] mem_mean, [4] mem_max
        predictions = {
            # averages the respective metric in the sample
            "cpu_request": round(sum([build[1] for build in sample]) / len(sample)),
            "mem_request": sum([build[3] for build in sample]) / len(sample),
        }

    ensure_higher_pred(predictions, build["package"]["name"])

    # warn if the prediction is below some thresholds
    if predictions["cpu_request"] < 0.25:
        logging.warning(f"Warning: CPU request for {build['hash']} is below 0.25 cores")
        predictions["cpu_request"] = DEFAULT_CPU_REQUEST
    if predictions["mem_request"] < 10_000_000:
        logging.warning(f"Warning: Memory request for {build['hash']} is below 10MB")
        predictions["mem_request"] = DEFAULT_MEM_REQUEST

    # convert predictions to k8s friendly format
    for k, v in predictions.items():
        if k.startswith("cpu"):
            predictions[k] = str(int(v))
        elif k.startswith("mem"):
            predictions[k] = k8s.convert_bytes(v)

    return {
        "hash": build["hash"],
        "variables": {
            # spack uses these env vars to set the resource requests
            # set them here at the last minute to avoid using these vars
            # and clogging up the code
            "KUBERNETES_CPU_REQUEST": predictions["cpu_request"],
            "KUBERNETES_MEMORY_REQUEST": predictions["mem_request"],
        },
    }


async def predict_bulk(db: aiosqlite.Connection, builds: list) -> list:
    """
    Handles a bulk request of builds

    args:
        builds: list of dicts (see predict_single)
    returns: see predict_single)
    """

    return await asyncio.gather(*(predict_single(db, build) for build in builds))


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
        "pkg_variants": build["package"]["variants"],
        "compiler_name": build["compiler"]["name"],
        "compiler_version": build["compiler"]["version"],
    }

    # ranked in order of priority, the params we would like to match on
    param_combos = [
        ("pkg_name", "pkg_version", "compiler_name", "compiler_version"),
        ("pkg_name", "compiler_name", "compiler_version"),
        ("pkg_name", "pkg_version", "compiler_name"),
        ("pkg_name", "compiler_name"),
        ("pkg_name", "pkg_version"),
        ("pkg_name",),
    ]

    for combo in param_combos:
        # filter by the params we want
        condition_values = [flat_build[param] for param in combo]
        # we want at least MIN_TRAIN_SAMPLE +1/= rows
        query = f"""
        SELECT pkg_variants, cpu_mean, cpu_max, mem_mean, mem_max FROM jobs
        WHERE ref='develop' AND {' AND '.join(f'{param}=?' for param in combo)}
        ORDER BY end DESC LIMIT {IDEAL_SAMPLE}
        """

        async with db.execute(query, condition_values) as cursor:
            sample = await cursor.fetchall()
            sample = filter_variants(sample, flat_build)
            # we can accept the sample if it's 1 shorter
            if len(sample) >= IDEAL_SAMPLE - 1:
                return sample
            # continue if we didn't find enough rows

    return []


def filter_variants(sample: list, build: dict) -> list:
    """
    Filter the sample to match the build's variants.
    """

    EXPENSIVE_VARIANTS = {
        "sycl",
        "mpi",
        "rocm",
        "cuda",
        "python",
        "fortran",
        "openmp",
        "hdf5",
    }

    matched_rows = []
    build_variants = spec.spec_variants(build["pkg_variants"])

    # we prefer exact matches but
    # we can accept the row if all the values of
    # EXPENSIVE_VARIANTS match
    for row in sample:
        row_variants = spec.spec_variants(row[0])
        if build_variants == row_variants:
            matched_rows.append(row)
        elif all(
            row_variants.get(variant) == build_variants.get(variant)
            for variant in EXPENSIVE_VARIANTS
        ):
            matched_rows.append(row)

    return matched_rows


def ensure_higher_pred(prediction: dict, pkg_name: str):
    """
    Ensure that the prediction is higher than the current allocation
    for the package. This will be removed in the future as we analyze
    the effectiveness of the prediction model.

    args:
        prediction: dict of predicted resource usage: cpu_request, mem_request
        pkg_name: str
    """

    cur_alloc = pkg_mappings.get(pkg_name)

    if cur_alloc:
        prediction["cpu_request"] = max(
            prediction["cpu_request"], cur_alloc["cpu_request"]
        )

        prediction["mem_request"] = max(
            prediction["mem_request"], cur_alloc["mem_request"]
        )
