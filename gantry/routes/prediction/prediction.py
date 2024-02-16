import asyncio
import logging

import aiosqlite

from gantry.routes.prediction.current_mapping import pkg_mappings
from gantry.util import k8s, spec

logger = logging.getLogger(__name__)

IDEAL_SAMPLE = 5
DEFAULT_CPU_REQUEST = 1.0
DEFAULT_MEM_REQUEST = 2 * 1_000_000_000  # 2GB in bytes
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
        # mapping of sample: [0] cpu_mean, [1] cpu_max, [2] mem_mean, [3] mem_max
        predictions = {
            # averages the respective metric in the sample
            # cpu should always be whole number
            "cpu_request": round(sum([build[0] for build in sample]) / len(sample)),
            "mem_request": sum([build[2] for build in sample]) / len(sample),
        }

    ensure_higher_pred(predictions, build["package"]["name"])

    # warn if the prediction is below some thresholds
    if predictions["cpu_request"] < 0.25:
        logger.warning(f"Warning: CPU request for {build['hash']} is below 0.25 cores")
        predictions["cpu_request"] = DEFAULT_CPU_REQUEST
    if predictions["mem_request"] < 10_000_000:
        logger.warning(f"Warning: Memory request for {build['hash']} is below 10MB")
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
    returns: see predict_single
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
    param_combos = (
        (
            "pkg_name",
            "pkg_variants",
            "pkg_version",
            "compiler_name",
            "compiler_version",
        ),
        ("pkg_name", "pkg_variants", "compiler_name", "compiler_version"),
        ("pkg_name", "pkg_variants", "pkg_version", "compiler_name"),
        ("pkg_name", "pkg_variants", "compiler_name"),
        ("pkg_name", "pkg_variants", "pkg_version"),
        ("pkg_name", "pkg_variants"),
    )

    async def select_sample(query: str, filters: dict, extra_params: list = []) -> list:
        async with db.execute(query, list(filters.values()) + extra_params) as cursor:
            sample = await cursor.fetchall()
            # we can accept the sample if it's 1 shorter
            if len(sample) >= IDEAL_SAMPLE - 1:
                return sample
        return []

    for combo in param_combos:
        filters = {param: flat_build[param] for param in combo}

        # the first attempt at getting a sample is to match on all the params
        # within this combo, variants included
        query = f"""
        SELECT cpu_mean, cpu_max, mem_mean, mem_max FROM jobs
        WHERE ref='develop' AND {' AND '.join(f'{param}=?' for param in filters.keys())}
        ORDER BY end DESC LIMIT {IDEAL_SAMPLE}
        """

        if sample := await select_sample(query, filters):
            return sample

        # if we are not able to get a sufficient sample, we'll try to filter
        # by expensive variants, rather than an exact variant match

        filters.pop("pkg_variants")
        variants = spec.spec_variants(flat_build["pkg_variants"])

        exp_variant_conditions = []
        exp_variant_values = []

        # iterate through all the expensive variants and create a set of conditions
        # for the select query
        for var in EXPENSIVE_VARIANTS:
            if var in variants:
                # if the client has queried for an expensive variant, we want to ensure
                # that the sample has the same exact value
                exp_variant_conditions.append(
                    f"json_extract(pkg_variants, '$.{var}')=?"
                )
                exp_variant_values.append(int(variants.get(var, 0)))
            else:
                # if an expensive variant was not queried for,
                # we want to make sure that the variant was not set within the sample
                # as we want to ensure that the sample is not biased towards
                # the presence of expensive variants (or lack thereof)
                exp_variant_conditions.append(
                    f"json_extract(pkg_variants, '$.{var}') IS NULL"
                )

        query = f"""
        SELECT cpu_mean, cpu_max, mem_mean, mem_max FROM jobs
        WHERE ref='develop' AND {' AND '.join(f'{param}=?' for param in filters.keys())}
        AND {' AND '.join(exp_variant_conditions)}
        ORDER BY end DESC LIMIT {IDEAL_SAMPLE}
        """

        if sample := await select_sample(query, filters, exp_variant_values):
            return sample

        # go to the next combo, we want to ensure that expensive variants
        # are taken into account

    return []


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
