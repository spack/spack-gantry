from gantry.clients.prometheus import util


class PrometheusNodeClient:
    def __init__(self, client):
        self.client = client

    async def get_uuid(self, hostname: str, time: float) -> dict:
        """
        args:
            hostname: node hostname
            time: time to query (unix timestamp)
        returns: dict of node info (UUID as of now)
        """

        res = await self.client.query(
            type="single",
            query={
                "metric": "kube_node_info",
                "filters": {"node": hostname},
            },
            time=time,
        )

        if not res:
            raise util.IncompleteData(f"node info is missing. hostname={hostname}")

        return res[0]["labels"]["system_uuid"]

    async def get_labels(self, hostname: str, time: float) -> dict:
        """
        args:
            hostname: node hostname
            time: time to query (unix timestamp)
        returns: dict of node labels
        """

        res = await self.client.query(
            type="single",
            query={
                "metric": "kube_node_labels",
                "filters": {"node": hostname},
            },
            time=time,
        )

        if not res:
            raise util.IncompleteData(f"node labels are missing. hostname={hostname}")

        labels = res[0]["labels"]

        return {
            "cores": float(labels["label_karpenter_k8s_aws_instance_cpu"]),
            "mem": float(labels["label_karpenter_k8s_aws_instance_memory"]),
            "arch": labels["label_kubernetes_io_arch"],
            "os": labels["label_kubernetes_io_os"],
            "instance_type": labels["label_node_kubernetes_io_instance_type"],
        }
