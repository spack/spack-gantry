BYTES_TO_MEGABYTES = 1 / 1_000_000

# these functions convert the predictions to k8s friendly format


def convert_bytes(bytes: float) -> str:
    """bytes to megabytes"""
    return str(int(bytes * BYTES_TO_MEGABYTES)) + "M"
