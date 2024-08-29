BYTES_TO_MEGABYTES = 1 / 1_000_000
CORES_TO_MILLICORES = 1_000

# these functions convert the predictions to k8s friendly format


def convert_bytes(bytes: float) -> str:
    """bytes to megabytes"""
    return str(int(round(bytes * BYTES_TO_MEGABYTES))) + "M"


def convert_cores(cores: float) -> str:
    """cores to millicores"""
    return str(int(round(cores * CORES_TO_MILLICORES))) + "m"
