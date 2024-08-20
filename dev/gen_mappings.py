# this script generates the (old) default resource mappings for the spackages in CI
# these values are used as a fallback source for the prediction model
# current_mapping.py will be created at OUTPUT
# be sure SPACK_ROOT is set and you are on the latest commit of develop

import os
from decimal import Decimal, InvalidOperation

import yaml

GANTRY_PATH = "/path/to/gantry"
OUTPUT = f"{GANTRY_PATH}/gantry/routes/prediction/current_mapping.py"


# https://github.com/kubernetes-client/python/blob/master/kubernetes/utils/quantity.py
# Apache License 2.0
def parse_quantity(quantity):
    """
    Parse kubernetes canonical form quantity like 200Mi to a decimal number.
    Supported SI suffixes:
    base1024: Ki | Mi | Gi | Ti | Pi | Ei
    base1000: n | u | m | "" | k | M | G | T | P | E

    Input:
    quantity: string. kubernetes canonical form quantity

    Returns:
    Decimal

    Raises:
    ValueError on invalid or unknown input
    """
    if isinstance(quantity, (int, float, Decimal)):
        return Decimal(quantity)

    exponents = {
        "n": -3,
        "u": -2,
        "m": -1,
        "K": 1,
        "k": 1,
        "M": 2,
        "G": 3,
        "T": 4,
        "P": 5,
        "E": 6,
    }

    quantity = str(quantity)
    number = quantity
    suffix = None
    if len(quantity) >= 2 and quantity[-1] == "i":
        if quantity[-2] in exponents:
            number = quantity[:-2]
            suffix = quantity[-2:]
    elif len(quantity) >= 1 and quantity[-1] in exponents:
        number = quantity[:-1]
        suffix = quantity[-1:]

    try:
        number = Decimal(number)
    except InvalidOperation:
        raise ValueError("Invalid number format: {}".format(number))

    if suffix is None:
        return number

    if suffix.endswith("i"):
        base = 1024
    elif len(suffix) == 1:
        base = 1000
    else:
        raise ValueError("{} has unknown suffix".format(quantity))

    # handle SI inconsistency
    if suffix == "ki":
        raise ValueError("{} has unknown suffix".format(quantity))

    if suffix[0] not in exponents:
        raise ValueError("{} has unknown suffix".format(quantity))

    exponent = Decimal(exponents[suffix[0]])
    return number * (base**exponent)


with open(
    f"{os.environ['SPACK_ROOT']}/share/spack/gitlab/cloud_pipelines/configs/linux/"
    "ci.yaml"
) as f:
    data = yaml.safe_load(f)

pkg_mappings = {}

for mapping in data["ci"]["pipeline-gen"][1]["submapping"]:
    vars = mapping["build-job"]["variables"]

    for pkg in mapping["match"]:
        pkg_mappings[pkg] = {
            "build_jobs": int(vars["SPACK_BUILD_JOBS"]),
            "cpu_request": float(parse_quantity(vars["KUBERNETES_CPU_REQUEST"])),
            "mem_request": float(parse_quantity(vars["KUBERNETES_MEMORY_REQUEST"])),
        }

# write the values of job_sizes and pkg_mappings to a file

# does not preserve old file contents
with open(OUTPUT, "w") as f:
    f.write("# fmt: off\n")
    f.write("# flake8: noqa\n")
    f.write(f"pkg_mappings = {pkg_mappings}\n")

print(f"Updated {OUTPUT} with new job sizes and package mappings")
