import json
import logging
import re
from datetime import datetime

import aiosqlite

from gantry.clients.gitlab import GitlabClient
from gantry.util.misc import insert_dict, setattrs, spec_variants
from gantry.clients.prometheus import (
    IncompleteData,
    PrometheusClient,
    process_resources,
    process_usage,
)


class Build:
    def __init__(
        self,
        status: str,
        name: str,
        id: int,
        start: str,
        end: str,
        retries: int,
        ref: str,
    ):
        self.status = status
        self.name = name
        self.id = id
        self.start = datetime.fromisoformat(start).timestamp()
        self.end = datetime.fromisoformat(end).timestamp()
        self.retries = retries
        self.ref = ref

    @property
    def valid_name(self) -> bool:
        """Returns True if the job is a build job, False otherwise."""

        # example: plumed@2.9.0 /i4u7p6u %gcc@11.4.0
        # arch=linux-ubuntu20.04-neoverse_v1 E4S ARM Neoverse V1
        job_name_pattern = re.compile(
            r"([^/ ]+)@([^/ ]+) /([^%]+) %([^ ]+) ([^ ]+) (.+)"
        )
        job_name_match = job_name_pattern.match(self.name)
        # groups: 1: name, 2: version, 3: hash, 4: compiler, 5: arch, 6: stack
        return bool(job_name_match)

    @property
    def midpoint(self) -> float:
        """Returns the midpoint of the job in unix time."""
        # prometheus is not guaranteed to have data at the exact start and end times
        # instead of creating an arbitrary buffer, ask for data in the middle of the job
        return (self.start + self.end) / 2

    async def is_ghost(self, db: aiosqlite.Connection, gl: GitlabClient) -> bool:
        """Returns the job's ghost status."""

        # prevent duplicate jobs from being inserted into the database
        async with db.execute(
            "select job_id from ghost_jobs where job_id = ?", (self.id,)
        ) as cursor:
            if await cursor.fetchone():
                # ghost job is already in the database
                return True

        log = await gl.job_log(self.id)
        ghost = "No need to rebuild" in log

        if ghost:
            await db.execute(("insert into ghost_jobs (name) values (?)"), (self.id,))

        return ghost

    async def in_db(self, db: aiosqlite.Connection) -> bool:
        """Checks if the job is already in the db."""

        async with db.execute(
            "select job_id from builds where job_id = ?", (self.id,)
        ) as cursor:
            found = bool(await cursor.fetchone())

        if found:
            logging.warning(f"job {self.id} already in database")

        return found

    async def get_annotations(self, prometheus: PrometheusClient):
        """Fetches the annotations and assigns multiple attributes."""

        annotations_res = await prometheus.query(
            type="single",
            query={
                "metric": "kube_pod_annotations",
                "filters": {"annotation_gitlab_ci_job_id": self.id},
            },
            time=self.midpoint,
        )

        if not annotations_res:
            raise IncompleteData(f"missing annotations for job {self.id}")

        annotations = annotations_res[0]["labels"]

        setattrs(
            self,
            pod=annotations["pod"],
            # if build jobs is not set, defaults to 16 due to spack settings
            build_jobs=annotations.get("annotation_metrics_spack_job_build_jobs", 16),
            arch=annotations["annotation_metrics_spack_job_spec_arch"],
            pkg_name=annotations["annotation_metrics_spack_job_spec_pkg_name"],
            pkg_version=annotations["annotation_metrics_spack_job_spec_pkg_version"],
            pkg_variants=spec_variants(
                annotations["annotation_metrics_spack_job_spec_variants"]
            ),
            compiler_name=annotations[
                "annotation_metrics_spack_job_spec_compiler_name"
            ],
            compiler_version=annotations[
                "annotation_metrics_spack_job_spec_compiler_version"
            ],
            stack=annotations["annotation_metrics_spack_ci_stack_name"],
        )

    async def get_resources(self, prometheus: PrometheusClient):
        """fetches pod requests and limits, and also sets the node hostname"""
        requests = process_resources(
            await prometheus.query(
                type="single",
                query={
                    "metric": "kube_pod_container_resource_requests",
                    "filters": {"container": "build", "pod": self.pod},
                },
                time=self.midpoint,
            ),
            self.id,
        )

        limits_res = await prometheus.query(
            type="single",
            query={
                "metric": "kube_pod_container_resource_limits",
                "filters": {"container": "build", "pod": self.pod},
            },
            time=self.midpoint,
        )

        if not limits_res:
            raise IncompleteData(f"missing limits for job {self.id}")

        # instead of needing to fetch the node where the pod ran from kube_pod_info
        # we can grab it from kube_pod_container_resource_limits
        # weirdly, it's not available in kube_pod_labels or annotations
        # https://github.com/kubernetes/kube-state-metrics/issues/1148

        self.node = limits_res[0]["labels"]["node"]
        limits = process_resources(limits_res, self.id)

        setattrs(
            self,
            cpu_request=requests["cpu"]["value"],
            mem_request=requests["memory"]["value"],
            cpu_limit=limits.get("cpu", {}).get("value"),
            mem_limit=limits["memory"]["value"],
        )

    async def get_usage(self, prometheus: PrometheusClient):
        """Sets resource usage attributes."""

        mem_usage = process_usage(
            await prometheus.query(
                type="range",
                query={
                    "metric": "container_memory_working_set_bytes",
                    "filters": {"container": "build", "pod": self.pod},
                },
                start=self.start,
                end=self.end,
            ),
            self.id,
        )

        cpu_usage = process_usage(
            await prometheus.query(
                type="range",
                custom_query=(
                    f"rate(container_cpu_usage_seconds_total{{"
                    f"pod='{self.pod}', container='build'}}[90s])"
                ),
                start=self.start,
                end=self.end,
            ),
            self.id,
        )

        setattrs(
            self,
            cpu_mean=cpu_usage["mean"],
            cpu_median=cpu_usage["median"],
            cpu_max=cpu_usage["max"],
            cpu_min=cpu_usage["min"],
            cpu_stddev=cpu_usage["stddev"],
            mem_mean=mem_usage["mean"],
            mem_median=mem_usage["median"],
            mem_max=mem_usage["max"],
            mem_min=mem_usage["min"],
            mem_stddev=mem_usage["stddev"],
        )

    async def insert(self, db: aiosqlite.Connection, vm_id: int) -> int:
        """Inserts the build into the database and returns its id."""

        async with db.execute(
            *insert_dict(
                "builds",
                {
                    "pod": self.pod,
                    "vm": vm_id,
                    "start": self.start,
                    "end": self.end,
                    "job_id": self.id,
                    "job_status": self.status,
                    "retries": self.retries,
                    "ref": self.ref,
                    "pkg_name": self.pkg_name,
                    "pkg_version": self.pkg_version,
                    "pkg_variants": json.dumps(self.pkg_variants),  # dict to string
                    "compiler_name": self.compiler_name,
                    "compiler_version": self.compiler_version,
                    "arch": self.arch,
                    "stack": self.stack,
                    "build_jobs": self.build_jobs,
                    "cpu_request": self.cpu_request,
                    "cpu_limit": self.cpu_limit,
                    "cpu_mean": self.cpu_mean,
                    "cpu_median": self.cpu_median,
                    "cpu_max": self.cpu_max,
                    "cpu_min": self.cpu_min,
                    "cpu_stddev": self.cpu_stddev,
                    "mem_request": self.mem_request,
                    "mem_limit": self.mem_limit,
                    "mem_mean": self.mem_mean,
                    "mem_median": self.mem_median,
                    "mem_max": self.mem_max,
                    "mem_min": self.mem_min,
                    "mem_stddev": self.mem_stddev,
                },
                # if the job somehow gets added into the db (pod+id being unique)
                # then ignore the insert
                ignore=True,
            )
        ) as cursor:
            return cursor.lastrowid
