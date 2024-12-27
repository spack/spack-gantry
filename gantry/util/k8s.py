from gantry.util.const import BYTES_IN_MB, MILLICORES_IN_CORES

# these functions convert the predictions to k8s friendly format
# https://kubernetes.io/docs/concepts/configuration/manage-resources-containers


def convert_bytes(bytes: float) -> str:
    """bytes to megabytes"""
    return str(int(round(bytes * BYTES_IN_MB))) + "M"


def convert_cores(cores: float) -> str:
    """cores to millicores"""
    return str(int(round(cores * MILLICORES_IN_CORES))) + "m"
