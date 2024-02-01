CORES_TO_MILLICORES = 1000
BYTES_TO_MEGABYTES = 1 / 1_000_000

# these functions convert the predictions to k8s friendly format

def convert_cores(cores: float) -> str:
    """cores to millicores"""
    return str(int(cores * CORES_TO_MILLICORES)) + "m"

def convert_bytes(bytes: float) -> str:
    """bytes to megabytes"""
    return str(int(bytes * BYTES_TO_MEGABYTES)) + "M"
