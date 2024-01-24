import aiosqlite

from gantry.util.misc import insert_dict, setattrs
from gantry.clients.prometheus import IncompleteData, PrometheusClient

MB_IN_BYTES = 1_000_000


class VM:
    def __init__(self, hostname: str, query_time: float):
        """
        args:
            hostname: the hostname of the VM
            query_time: any point during VM runtime, usually grabbed from build
        """
        self.hostname = hostname
        self.query_time = query_time

    async def db_id(
        self, db: aiosqlite.Connection, prometheus: PrometheusClient
    ) -> int | None:
        """
        Returns the id of the vm if it exists in the database, otherwise returns None.
        Also sets the uuid of the vm.
        """
        vm_info = await prometheus.query(
            type="single",
            query={
                "metric": "kube_node_info",
                "filters": {"node": self.hostname},
            },
            time=self.query_time,
        )

        if not vm_info:
            raise IncompleteData(f"missing vm info for {self.hostname}")

        self.uuid = vm_info[0]["labels"]["system_uuid"]

        # look for the vm in the database
        async with db.execute(
            "select id from vms where uuid = ?", (self.uuid,)
        ) as cursor:
            old_vm = await cursor.fetchone()

            if old_vm:
                return old_vm[0]

        return None

    async def get_labels(self, prometheus: PrometheusClient):
        """Sets multiple attributes of the VM based on its labels."""

        vm_labels_res = await prometheus.query(
            type="single",
            query={
                "metric": "kube_node_labels",
                "filters": {"node": self.hostname},
            },
            time=self.query_time,
        )

        if not vm_labels_res:
            raise IncompleteData(f"missing vm labels for {self.hostname}")

        labels = vm_labels_res[0]["labels"]

        setattrs(
            self,
            cores=float(labels["label_karpenter_k8s_aws_instance_cpu"]),
            mem=float(labels["label_karpenter_k8s_aws_instance_memory"]),
            arch=labels["label_kubernetes_io_arch"],
            os=labels["label_kubernetes_io_os"],
            instance_type=labels["label_node_kubernetes_io_instance_type"],
        )

    async def insert(self, db: aiosqlite.Connection) -> int:
        """Inserts the VM into the database and returns its id."""
        async with db.execute(
            *insert_dict(
                "vms",
                {
                    "uuid": self.uuid,
                    "hostname": self.hostname,
                    "cores": self.cores,
                    # convert to bytes to be consistent with other resource metrics
                    "mem": self.mem * MB_IN_BYTES,
                    "arch": self.arch,
                    "os": self.os,
                    "instance_type": self.instance_type,
                },
                # deal with races
                ignore=True,
            )
        ) as cursor:
            pk = cursor.lastrowid

        if pk == 0:
            # the ignore part of the query was triggered, some other call
            # must have inserted the vm before this one
            async with db.execute(
                "select id from vms where uuid = ?", (self.uuid,)
            ) as cursor:
                pk_res = await cursor.fetchone()
                pk = pk_res[0]

        return pk
