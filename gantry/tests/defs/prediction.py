# flake8: noqa
# fmt: off

from gantry.util.spec import parse_alloc_spec

NORMAL_BUILD = parse_alloc_spec(
    "py-torch@2.2.1 ~caffe2+cuda+cudnn~debug+distributed+fbgemm+gloo+kineto~magma~metal+mkldnn+mpi~nccl+nnpack+numa+numpy+onnx_ml+openmp+qnnpack~rocm+tensorpipe~test+valgrind+xnnpack build_system=python_pip cuda_arch=80%gcc@11.4.0"
)

# everything in NORMAL_BUILD["package"]["variants"] except removing build_system=python_pip
# in order to test the expensive variants filter
EXPENSIVE_VARIANT_BUILD = parse_alloc_spec(
    "py-torch@2.2.1 ~caffe2+cuda+cudnn~debug+distributed+fbgemm+gloo+kineto~magma~metal+mkldnn+mpi~nccl+nnpack+numa+numpy+onnx_ml+openmp+qnnpack~rocm+tensorpipe~test+valgrind+xnnpack cuda_arch=80%gcc@11.4.0"
)

# no variants should match this, so we expect the default prediction
BAD_VARIANT_BUILD = parse_alloc_spec(
    "py-torch@2.2.1 +no~expensive~variants+match%gcc@11.4.0"
)

# calculated by running the baseline prediction algorithm on the sample data in gantry/tests/sql/insert_prediction.sql
NORMAL_PREDICTION = {
    "variables": {
        "KUBERNETES_CPU_REQUEST": "11.8",
        "KUBERNETES_MEMORY_REQUEST": "9576M",
    },
}

# this is what will get returned when there are no samples in the database
# that match what the client wants
DEFAULT_PREDICTION = {
    "variables": {
        "KUBERNETES_CPU_REQUEST": "1.0",
        "KUBERNETES_MEMORY_REQUEST": "2000M",
    },
}
