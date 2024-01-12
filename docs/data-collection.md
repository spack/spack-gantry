# Data Collection

Job metadata is retrieved through the Spack Prometheus service (https://prometheus.spack.io).

Links to documentation for metrics available:
- [node](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/node-metrics.md)
- [pod](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/pod-metrics.md)
- [container](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)

To programmatically access Prometheus, one must send a copy of a session cookie with their request. In the future, we would be able to use a generated API token to authenticate.
