import logging

import aiosqlite

from gantry.util import k8s

logger = logging.getLogger(__name__)

IDEAL_SAMPLE = 5
DEFAULT_CPU_REQUEST = 1
DEFAULT_MEM_REQUEST = 2 * 1_000_000_000  # 2GB in bytes
DEFAULT_CPU_LIMIT = 5
DEFAULT_MEM_LIMIT = 5 * 1_000_000_000
MEM_LIMIT_BUMP = 1.2
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


async def predict(db: aiosqlite.Connection, spec: dict) -> dict:
    """
    Predict the resource usage of a spec

    args:
        spec: dict that contains pkg_name, pkg_version, pkg_variants,
        compiler_name, compiler_version
    returns:
        dict of predicted resource usage: cpu_request, mem_request
        CPU in millicore, mem in MB
    """

    sample = await get_sample(db, spec)
    predictions = {}
    if not sample:
        predictions = {
            "cpu_request": DEFAULT_CPU_REQUEST,
            "mem_request": DEFAULT_MEM_REQUEST,
            "cpu_limit": DEFAULT_CPU_LIMIT,
            "mem_limit": DEFAULT_MEM_LIMIT,
            "build_jobs": DEFAULT_CPU_REQUEST,
        }
    else:
        # mapping of sample: [0] cpu_mean, [1] cpu_max, [2] mem_mean, [3] mem_max
        n = len(sample)
        predictions = {
            "cpu_request": sum([build[0] for build in sample]) / n,
            "mem_request": sum([build[2] for build in sample]) / n,
            "cpu_limit": sum([build[1] for build in sample]) / n,
            "mem_limit": max([build[3] for build in sample]) * MEM_LIMIT_BUMP,
        }
        # build jobs cannot be less than 1
        predictions["build_jobs"] = max(1, round(predictions["cpu_request"]))

    if strategy == "ensure_higher":
        ensure_higher_pred(predictions, spec["pkg_name"])

    # convert predictions to k8s friendly format
    for k, v in predictions.items():
        if k.startswith("cpu"):
            predictions[k] = k8s.convert_cores(v)
        elif k.startswith("mem"):
            predictions[k] = k8s.convert_bytes(v)

    return {
        "variables": {
            "KUBERNETES_CPU_REQUEST": predictions["cpu_request"],
            "KUBERNETES_MEMORY_REQUEST": predictions["mem_request"],
            "KUBERNETES_CPU_LIMIT": predictions["cpu_limit"],
            "KUBERNETES_MEMORY_LIMIT": predictions["mem_limit"],
            "SPACK_BUILD_JOBS": predictions["build_jobs"],
            "CI_JOB_SIZE": "custom",
        },
    }


async def get_sample(db: aiosqlite.Connection, spec: dict) -> list:
    """
    Selects a sample of builds to use for prediction

    args:
        spec: see predict
    returns:
        list of lists with cpu_mean, cpu_max, mem_mean, mem_max
    """

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
        filters = {param: spec[param] for param in combo}

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

        exp_variant_conditions = []
        exp_variant_values = []

        # iterate through all the expensive variants and create a set of conditions
        # for the select query
        for var in EXPENSIVE_VARIANTS:
            variant_value = spec["pkg_variants_dict"].get(var)

            # check against specs where hdf5=none like quantum-espresso
            if isinstance(variant_value, (bool, int)):
                # if the client has queried for an expensive variant, we want to ensure
                # that the sample has the same exact value
                exp_variant_conditions.append(
                    f"json_extract(pkg_variants, '$.{var}')=?"
                )

                exp_variant_values.append(int(variant_value))
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

    return []
