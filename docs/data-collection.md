# Data Collection

Job metadata is retrieved through the Spack Prometheus service (https://prometheus.spack.io).

Gantry exposes a webhook handler at `/v1/collection` which will accept a job status payload from Gitlab and collect build attributes and usage, submitting to the database.

See the `migrations` folder for the complete database schema.

## Units

Memory usage is stored in bytes, while CPU usage is stored in cores. Pay special attention if you are interacting with relevant fields if you are performing calculations or sending data from these fields to Kubernetes or another external service. They may expect these values in different units.

------

Links to documentation for metrics available:
- [node](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/node-metrics.md)
- [pod](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/pod-metrics.md)
- [container](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)
