# centralized constants for the project

# resources
MB_IN_BYTES = 1_000_000
BYTES_IN_MB = 1 / MB_IN_BYTES
MILLICORES_IN_CORES = 1_000

# spec
# example: emacs@29.2 +json+native+treesitter arch=x86_64%gcc@12.3.0
# this regex accommodates versions made up of any non-space characters
SPACK_SPEC_PATTERN = r"(.+?)@(\S+)\s+(.+?)\s+arch=(\S+)%([\w-]+)@(\S+)"

# gitlab
# sends dates in 2021-02-23 02:41:37 UTC format
# documentation says they use iso 8601, but they don't consistently apply it
# https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html#job-events
GITLAB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

# collection
# all build jobs will match this pattern (eg: stage-1 but not stage-index)
BUILD_STAGE_REGEX = r"^stage-\d+$"

# prediction
TRAINING_SAMPLES = 5  # number of past builds to use for prediction
DEFAULT_CPU_REQUEST = 1  # cores
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
