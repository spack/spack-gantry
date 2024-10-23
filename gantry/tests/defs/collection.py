# flake8: noqa
# fmt: off

INVALID_STAGE = "stage-generate"
# uo runners are not supported
INVALID_RUNNER = {"description": "uo-blabla1821"}
INVALID_JOB_STATUS = "failure"
GHOST_JOB_LOG = "No need to rebuild"
VALID_JOB_LOG = "some log"

VALID_JOB = {
    "build_status": "success",
    "build_stage": "stage-1",
    "build_id": 9892514,  # not used in testing unless it already exists in the db
    "build_started_at": "2024-01-24 17:24:06 UTC",
    "build_finished_at": "2024-01-24 17:47:00 UTC",
    "ref": "pr42264_bugfix/mathomp4/hdf5-appleclang15",
    "runner": {"description": "aws"},
}

FAILED_JOB = {
    "build_status": "failed",
    "build_stage": "stage-1",
    "build_id": 9892514,  # not used in testing unless it already exists in the db
    "build_started_at": "2024-01-24 17:24:06 UTC",
    "build_finished_at": "2024-01-24 17:47:00 UTC",
    "ref": "pr42264_bugfix/mathomp4/hdf5-appleclang15",
    "runner": {"description": "aws"},
}


# used to compare successful insertions
# run SELECT * FROM table_name WHERE id = 1; from python sqlite api and grab fetchone() result
INSERTED_JOB = (1, 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 1, 1706117046, 1706118420, 9892514, 'success', 'pr42264_bugfix/mathomp4/hdf5-appleclang15', 'gmsh', '4.8.4', '{"alglib": true, "cairo": false, "cgns": true, "compression": true, "eigen": false, "external": false, "fltk": true, "gmp": true, "hdf5": false, "ipo": false, "med": true, "metis": true, "mmg": true, "mpi": true, "netgen": true, "oce": true, "opencascade": false, "openmp": false, "petsc": false, "privateapi": false, "shared": true, "slepc": false, "tetgen": true, "voropp": true, "build_system": "cmake", "build_type": "Release", "generator": "make"}', 'gcc', '11.4.0', 'linux', 'e4s', 16, 0.75, None, 1.899768349523097, 0.2971597591741076, 4.128116379389054, 0.2483743618267752, 1.7602635378120381, 2000000000.0, 48000000000.0, 143698407.6190476, 2785280.0, 594620416.0, 2785280.0, 252073065.82263485, 0, 0)
INSERTED_NODE = (1, 'ec253b04-b1dc-f08b-acac-e23df83b3602', 'ip-192-168-86-107.ec2.internal', 24.0, 196608000000.0, 'amd64', 'linux', 'i3en.6xlarge')

# these were obtained by executing the respective queries to Prometheus and capturing the JSON output
# or the raw output of PrometheusClient._query
VALID_ANNOTATIONS = {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {'__name__': 'kube_pod_annotations', 'annotation_gitlab_ci_job_id': '9892514', 'annotation_metrics_spack_ci_stack_name': 'e4s', 'annotation_metrics_spack_job_spec_arch': 'linux', 'annotation_metrics_spack_job_spec_compiler_name': 'gcc', 'annotation_metrics_spack_job_spec_compiler_version': '11.4.0', 'annotation_metrics_spack_job_retry_count': '0', 'annotation_metrics_spack_job_spec_pkg_name': 'gmsh', 'annotation_metrics_spack_job_spec_pkg_version': '4.8.4', 'annotation_metrics_spack_job_spec_variants': '+alglib~cairo+cgns+compression~eigen~external+fltk+gmp~hdf5~ipo+med+metis+mmg+mpi+netgen+oce~opencascade~openmp~petsc~privateapi+shared~slepc+tetgen+voropp build_system=cmake build_type=Release generator=make', 'container': 'kube-state-metrics', 'endpoint': 'http', 'instance': '192.168.164.84:8080', 'job': 'kube-state-metrics', 'namespace': 'pipeline', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'service': 'kube-prometheus-stack-kube-state-metrics', 'uid': 'd7aa13e0-998c-4f21-b1d6-62781f4980b0'}, 'value': [1706117733, '1']}]}}
VALID_RESOURCE_REQUESTS = {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {'__name__': 'kube_pod_container_resource_requests', 'container': 'build', 'endpoint': 'http', 'instance': '192.168.164.84:8080', 'job': 'kube-state-metrics', 'namespace': 'pipeline', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'resource': 'cpu', 'service': 'kube-prometheus-stack-kube-state-metrics', 'uid': 'd7aa13e0-998c-4f21-b1d6-62781f4980b0', 'unit': 'core'}, 'value': [1706117733, '0.75']}, {'metric': {'__name__': 'kube_pod_container_resource_requests', 'container': 'build', 'endpoint': 'http', 'instance': '192.168.164.84:8080', 'job': 'kube-state-metrics', 'namespace': 'pipeline', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'resource': 'memory', 'service': 'kube-prometheus-stack-kube-state-metrics', 'uid': 'd7aa13e0-998c-4f21-b1d6-62781f4980b0', 'unit': 'byte'}, 'value': [1706117733, '2000000000']}]}}
VALID_RESOURCE_LIMITS = {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {'__name__': 'kube_pod_container_resource_limits', 'container': 'build', 'endpoint': 'http', 'instance': '192.168.164.84:8080', 'job': 'kube-state-metrics', 'namespace': 'pipeline', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'resource': 'memory', 'service': 'kube-prometheus-stack-kube-state-metrics', 'uid': 'd7aa13e0-998c-4f21-b1d6-62781f4980b0', 'unit': 'byte'}, 'value': [1706117733, '48000000000']}]}}
VALID_MEMORY_USAGE = {'status': 'success', 'data': {'resultType': 'matrix', 'result': [{'metric': {'__name__': 'container_memory_working_set_bytes', 'container': 'build', 'endpoint': 'https-metrics', 'id': '/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd7aa13e0_998c_4f21_b1d6_62781f4980b0.slice/cri-containerd-48a5e9e7d46655e73ba119fa16b65fa94ceed23c55157db8269b0b12f18f55d1.scope', 'image': 'ghcr.io/spack/ubuntu20.04-runner-amd64-gcc-11.4:2023.08.01', 'instance': '192.168.86.107:10250', 'job': 'kubelet', 'metrics_path': '/metrics/cadvisor', 'name': '48a5e9e7d46655e73ba119fa16b65fa94ceed23c55157db8269b0b12f18f55d1', 'namespace': 'pipeline', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'service': 'kube-prometheus-stack-kubelet'}, 'values': [[1706117115, '2785280'], [1706117116, '2785280'], [1706117117, '2785280'], [1706117118, '2785280'], [1706117119, '2785280'], [1706117120, '2785280'], [1706117121, '2785280'], [1706117122, '2785280'], [1706117123, '2785280'], [1706117124, '2785280'], [1706117125, '2785280'], [1706117126, '2785280'], [1706117127, '2785280'], [1706117128, '2785280'], [1706117129, '2785280'], [1706117130, '2785280'], [1706118416, '594620416'], [1706118417, '594620416'], [1706118418, '594620416'], [1706118419, '594620416'], [1706118420, '594620416']]}]}}
VALID_CPU_USAGE = {'status': 'success', 'data': {'resultType': 'matrix', 'result': [{'metric': {'container': 'build', 'cpu': 'total', 'endpoint': 'https-metrics', 'id': '/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd7aa13e0_998c_4f21_b1d6_62781f4980b0.slice/cri-containerd-48a5e9e7d46655e73ba119fa16b65fa94ceed23c55157db8269b0b12f18f55d1.scope', 'image': 'ghcr.io/spack/ubuntu20.04-runner-amd64-gcc-11.4:2023.08.01', 'instance': '192.168.86.107:10250', 'job': 'kubelet', 'metrics_path': '/metrics/cadvisor', 'name': '48a5e9e7d46655e73ba119fa16b65fa94ceed23c55157db8269b0b12f18f55d1', 'namespace': 'pipeline', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'service': 'kube-prometheus-stack-kubelet'}, 'values': [[1706117145, '0.2483743618267752'], [1706117146, '0.25650526138466395'], [1706117147, '0.26463616094255266'], [1706117148, '0.2727670605004414'], [1706117149, '0.28089796005833007'], [1706117150, '0.2890288596162188'], [1706117151, '0.2971597591741076'], [1706117357, '3.7319005481816236'], [1706117358, '3.7319005481816236'], [1706117359, '3.7319005481816236'], [1706117360, '3.7319005481816245'], [1706117361, '3.7319005481816245'], [1706118420, '4.128116379389054']]}]}}
VALID_NODE_INFO = {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {'__name__': 'kube_node_info', 'container': 'kube-state-metrics', 'container_runtime_version': 'containerd://1.7.2', 'endpoint': 'http', 'instance': '192.168.164.84:8080', 'internal_ip': '192.168.86.107', 'job': 'kube-state-metrics', 'kernel_version': '5.10.205-195.804.amzn2.x86_64', 'kubelet_version': 'v1.27.9-eks-5e0fdde', 'kubeproxy_version': 'v1.27.9-eks-5e0fdde', 'namespace': 'monitoring', 'node': 'ip-192-168-86-107.ec2.internal', 'os_image': 'Amazon Linux 2', 'pod': 'kube-prometheus-stack-kube-state-metrics-dbd66d8c7-6ftw8', 'provider_id': 'aws:///us-east-1c/i-0fe9d9c99fdb3631d', 'service': 'kube-prometheus-stack-kube-state-metrics', 'system_uuid': 'ec253b04-b1dc-f08b-acac-e23df83b3602'}, 'value': [1706117733, '1']}]}}
VALID_NODE_LABELS = {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {'__name__': 'kube_node_labels', 'container': 'kube-state-metrics', 'endpoint': 'http', 'instance': '192.168.164.84:8080', 'job': 'kube-state-metrics', 'label_beta_kubernetes_io_arch': 'amd64', 'label_beta_kubernetes_io_instance_type': 'i3en.6xlarge', 'label_beta_kubernetes_io_os': 'linux', 'label_failure_domain_beta_kubernetes_io_region': 'us-east-1', 'label_failure_domain_beta_kubernetes_io_zone': 'us-east-1c', 'label_k8s_io_cloud_provider_aws': 'ceb9f9cc8e47252a6f7fe7d6bded2655', 'label_karpenter_k8s_aws_instance_category': 'i', 'label_karpenter_k8s_aws_instance_cpu': '24', 'label_karpenter_k8s_aws_instance_encryption_in_transit_supported': 'true', 'label_karpenter_k8s_aws_instance_family': 'i3en', 'label_karpenter_k8s_aws_instance_generation': '3', 'label_karpenter_k8s_aws_instance_hypervisor': 'nitro', 'label_karpenter_k8s_aws_instance_local_nvme': '15000', 'label_karpenter_k8s_aws_instance_memory': '196608', 'label_karpenter_k8s_aws_instance_network_bandwidth': '25000', 'label_karpenter_k8s_aws_instance_pods': '234', 'label_karpenter_k8s_aws_instance_size': '6xlarge', 'label_karpenter_sh_capacity_type': 'spot', 'label_karpenter_sh_initialized': 'true', 'label_karpenter_sh_provisioner_name': 'glr-x86-64-v4', 'label_kubernetes_io_arch': 'amd64', 'label_kubernetes_io_hostname': 'ip-192-168-86-107.ec2.internal', 'label_kubernetes_io_os': 'linux', 'label_node_kubernetes_io_instance_type': 'i3en.6xlarge', 'label_spack_io_pipeline': 'true', 'label_spack_io_x86_64': 'v4', 'label_topology_ebs_csi_aws_com_zone': 'us-east-1c', 'label_topology_kubernetes_io_region': 'us-east-1', 'label_topology_kubernetes_io_zone': 'us-east-1c', 'namespace': 'monitoring', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'kube-prometheus-stack-kube-state-metrics-dbd66d8c7-6ftw8', 'service': 'kube-prometheus-stack-kube-state-metrics'}, 'value': [1706117733, '1']}]}}
# TODO FIX THIS WHEN WE KNOW THE RIGHT METHOD
OOM_KILLED = {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {'__name__': 'kube_pod_container_status_last_terminated_reason', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'container': 'build', 'reason': 'OOMKilled'}, 'value': [1706117733, '1']}]}}
NOT_OOM_KILLED = {'status': 'success', 'data': {'resultType': 'vector', 'result': []}}
# modified version of VALID_MEMORY_USAGE to make the mean/stddev 0
INVALID_MEMORY_USAGE = {'status': 'success', 'data': {'resultType': 'matrix', 'result': [{'metric': {'__name__': 'container_memory_working_set_bytes', 'container': 'build', 'endpoint': 'https-metrics', 'id': '/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd7aa13e0_998c_4f21_b1d6_62781f4980b0.slice/cri-containerd-48a5e9e7d46655e73ba119fa16b65fa94ceed23c55157db8269b0b12f18f55d1.scope', 'image': 'ghcr.io/spack/ubuntu20.04-runner-amd64-gcc-11.4:2023.08.01', 'instance': '192.168.86.107:10250', 'job': 'kubelet', 'metrics_path': '/metrics/cadvisor', 'name': '48a5e9e7d46655e73ba119fa16b65fa94ceed23c55157db8269b0b12f18f55d1', 'namespace': 'pipeline', 'node': 'ip-192-168-86-107.ec2.internal', 'pod': 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 'service': 'kube-prometheus-stack-kubelet'}, 'values': [[1706117115, '0']]}]}}

# pipeline definitions
SUCCESSFUL_PIPELINE = {
    "object_attributes": {
        "status": "success",
        "ref": "pr42264_bugfix/mathomp4/hdf5-appleclang15",
    }
}

FAILED_PIPELINE = {
    "object_attributes": {
        "status": "failed",
        "ref": "pr42264_bugfix/mathomp4/hdf5-appleclang15",
    },
    "builds": [
        {"id": 9892514, "stage": "stage-1", "status": "failed", "runner": {"description": "aws"}, "started_at": "2024-01-24 17:24:06 UTC", "finished_at": "2024-01-24 17:47:00 UTC"},
    ]
}

INSERTED_OOM_JOB = (1, 'runner-hwwb-i3u-project-2-concurrent-1-s10tq41z', 1, 1706117046, 1706118420, 9892514, 'failed', 'pr42264_bugfix/mathomp4/hdf5-appleclang15', 'gmsh', '4.8.4', '{"alglib": true, "cairo": false, "cgns": true, "compression": true, "eigen": false, "external": false, "fltk": true, "gmp": true, "hdf5": false, "ipo": false, "med": true, "metis": true, "mmg": true, "mpi": true, "netgen": true, "oce": true, "opencascade": false, "openmp": false, "petsc": false, "privateapi": false, "shared": true, "slepc": false, "tetgen": true, "voropp": true, "build_system": "cmake", "build_type": "Release", "generator": "make"}', 'gcc', '11.4.0', 'linux', 'e4s', 16, 0.75, None, 1.899768349523097, 0.2971597591741076, 4.128116379389054, 0.2483743618267752, 1.7602635378120381, 2000000000.0, 48000000000.0, 143698407.6190476, 2785280.0, 594620416.0, 2785280.0, 252073065.82263485, 1, 0)
