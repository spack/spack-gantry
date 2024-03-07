# flake8: noqa
# fmt: off

NORMAL_BUILD = {
    "hash": "testing",
    "package": {
        "name": "py-torch",
        "version": "2.2.1",
        "variants": "~caffe2+cuda+cudnn~debug+distributed+fbgemm+gloo+kineto~magma~metal+mkldnn+mpi~nccl+nnpack+numa+numpy+onnx_ml+openmp+qnnpack~rocm+tensorpipe~test+valgrind+xnnpack build_system=python_pip cuda_arch=80",
    },
    "compiler": {
        "name": "gcc",
        "version": "11.4.0",
    },
}

# everything in NORMAL_BUILD["package"]["variants"] except removing build_system=python_pip
# in order to test the expensive variants filter
EXPENSIVE_VARIANT_BUILD = {
    "hash": "testing",
    "package": {
        "name": "py-torch",
        "version": "2.2.1",
        "variants": "~caffe2+cuda+cudnn~debug+distributed+fbgemm+gloo+kineto~magma~metal+mkldnn+mpi~nccl+nnpack+numa+numpy+onnx_ml+openmp+qnnpack~rocm+tensorpipe~test+valgrind+xnnpack cuda_arch=80",
    },
    "compiler": {
        "name": "gcc",
        "version": "11.4.0",
    },
}

# no variants should match this, so we expect the default prediction
BAD_VARIANT_BUILD = {
    "hash": "testing",
    "package": {
        "name": "py-torch",
        "version": "2.2.1",
        "variants": "+no~expensive~variants+match",
    },
    "compiler": {
        "name": "gcc",
        "version": "11.4.0",
    },
}

# calculated by running the baseline prediction algorithm on the sample data in gantry/tests/sql/insert_prediction.sql
NORMAL_PREDICTION = {
    "hash": "testing",
    "variables": {
        "KUBERNETES_CPU_REQUEST": "12",
        "KUBERNETES_MEMORY_REQUEST": "9576M",
    },
}


# this is what will get returned when there are no samples in the database
# that match what the client wants
DEFAULT_PREDICTION = {
    "hash": "testing",
    "variables": {
        "KUBERNETES_CPU_REQUEST": "1",
        "KUBERNETES_MEMORY_REQUEST": "2000M",
    },
}
