BYTES_TO_MEGABYTES = 1 / 1_000_000
CORES_TO_MILLICORES = 1_000

# https://kubernetes.io/docs/concepts/configuration/manage-resources-containers


def convert_allocations(allocations: dict) -> dict:
    """converts the allocations to k8s friendly format"""
    for k, v in allocations.items():
        if "cpu" in k.lower():
            allocations[k] = convert_cores(v)
        elif "mem" in k.lower():
            allocations[k] = convert_bytes(v)
    return allocations


def convert_bytes(bytes: float) -> str:
    """bytes to megabytes"""
    return str(int(round(bytes * BYTES_TO_MEGABYTES))) + "M"


def convert_cores(cores: float) -> str:
    """cores to millicores"""
    return str(int(round(cores * CORES_TO_MILLICORES))) + "m"
