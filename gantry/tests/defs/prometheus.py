# flake8: noqa
# fmt: off

QUERY_DICT = query={"metric": "kube_pod_annotations","filters": {"annotation_gitlab_ci_job_id": 1}}
QUERY_STR = "rate(container_cpu_usage_seconds_total{pod='1', container='build'}[90s])"

# encoded versions of the above that were put through the original version of process_query
ENCODED_QUERY_DICT = "kube_pod_annotations%7Bannotation_gitlab_ci_job_id%3D%221%22%7D"
ENCODED_QUERY_STR = "rate%28container_cpu_usage_seconds_total%7Bpod%3D%271%27%2C%20container%3D%27build%27%7D%5B90s%5D%29"

# this will not be parsed as a query
INVALID_QUERY = 1
