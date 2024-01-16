import json
import logging
import math
import re
import statistics
from datetime import datetime

from utils.gitlab import GitlabClient
from utils.misc import db_insert, spec_variants
from utils.prometheus import PrometheusClient


class InvalidDataError(Exception):
    pass


async def fetch_job(job: dict, db) -> dict:
    gitlab = GitlabClient()
    prometheus = PrometheusClient()

    if job["build_status"] not in ("success", "failed"):
        return

    job_name_pattern = re.compile(r"([^/ ]+)@([^/ ]+) /([^%]+) %([^ ]+) ([^ ]+) (.+)")
    job_name_match = job_name_pattern.match(job["build_name"])
    if not job_name_match:
        # generate jobs, non build jobs, etc
        return

    # check if job has already been inserted into the database
    async with db.execute(
        "select job_id from builds where job_id = ?", (job["build_id"],)
    ) as cursor:
        if await cursor.fetchone():
            logging.info(f"job {job['build_id']} already in database")
            return

    job_log = await gitlab.job_log(job["build_id"])
    if is_ghost(job_log):
        await db.execute(
            ("insert into ghost_jobs (name) values (?)"), (job["build_id"],)
        )
        return

    job["start"] = datetime.fromisoformat(job["build_started_at"]).timestamp()
    job["end"] = datetime.fromisoformat(job["build_finished_at"]).timestamp()

    # prometheus is not guaranteed to have data at the exact start and end times
    # instead of creating an arbitrary buffer, ask for data in the middle of the job
    query_time = (job["end"] + job["start"]) / 2

    pod_annotations_res = await prometheus.query(
        type="single",
        query={
            "metric": "kube_pod_annotations",
            "filters": {"annotation_gitlab_ci_job_id": job["build_id"]},
        },
        time=query_time,
    )

    job.update(
        {
            "pod": pod_annotations_res[0]["labels"]["pod"],
            "build_jobs": int(
                pod_annotations_res[0]["labels"][
                    "annotation_metrics_spack_job_build_jobs"
                ]
            ),
            "arch": pod_annotations_res[0]["labels"][
                "annotation_metrics_spack_job_spec_arch"
            ],
            "pkg_name": pod_annotations_res[0]["labels"][
                "annotation_metrics_spack_job_spec_pkg_name"
            ],
            "pkg_version": pod_annotations_res[0]["labels"][
                "annotation_metrics_spack_job_spec_pkg_version"
            ],
            "pkg_variants": spec_variants(
                pod_annotations_res[0]["labels"][
                    "annotation_metrics_spack_job_spec_variants"
                ]
            ),
            "compiler_name": pod_annotations_res[0]["labels"][
                "annotation_metrics_spack_job_spec_compiler_name"
            ],
            "compiler_version": pod_annotations_res[0]["labels"][
                "annotation_metrics_spack_job_spec_compiler_version"
            ],
            "stack": job_name_match.group(6),
        }
    )

    job_requests_res = await prometheus.query(
        type="single",
        query={
            "metric": "kube_pod_container_resource_requests",
            "filters": {"container": "build", "pod": job["pod"]},
        },
        time=query_time,
    )

    job_limits_res = await prometheus.query(
        type="single",
        query={
            "metric": "kube_pod_container_resource_limits",
            "filters": {"container": "build", "pod": job["pod"]},
        },
        time=query_time,
    )

    mem_usage = process_usage(
        await prometheus.query(
            type="range",
            query={
                "metric": "container_memory_working_set_bytes",
                "filters": {"container": "build", "pod": job["pod"]},
            },
            start=job["start"],
            end=job["end"],
        ),
        job["build_id"],
    )

    cpu_usage = process_usage(
        await prometheus.query(
            type="range",
            custom_query=(
                f"rate(container_cpu_usage_seconds_total{{"
                f"pod='{job['pod']}', container='build'}}[90s])"
            ),
            start=job["start"],
            end=job["end"],
        ),
        job["build_id"],
    )

    if job["build_status"] == "failed":
        oom_status = prometheus.query(
            type="range",
            query={
                "metric": "kube_pod_container_status_last_terminated_reason",
                "filters": {
                    "container": "build",
                    "pod": job["pod"],
                    "reason": "OOMKilled",
                },
            },
            start=job["start"],
            end=job["end"] + 10 * 60,  # give a 10 minute buffer
        )
        # TODO retry the job if OOM, do not return as we still want to save the build
        if not oom_status:
            return

    # instead of needing to fetch the node where the pod ran from kube_pod_info
    # we can grab it from kube_pod_container_resource_limits
    # weirdly, it's not available in kube_pod_labels or annotations
    # https://github.com/kubernetes/kube-state-metrics/issues/1148
    vm = await fetch_vm(job_limits_res[0]["labels"]["node"], query_time, db)
    requests = process_resources_res(job_requests_res)
    limits = process_resources_res(job_limits_res)

    await db.execute(
        *db_insert(
            "builds",
            (
                None,
                job["pod"],
                vm,
                job["start"],
                job["end"],
                job["build_id"],
                job["build_status"],
                job["retries_count"],
                job["ref"],
                job["pkg_name"],
                job["pkg_version"],
                json.dumps(job["pkg_variants"]),  # dict to string
                job["compiler_name"],
                job["compiler_version"],
                job["arch"],
                job["stack"],
                job["build_jobs"],
                requests["cpu"]["value"],
                # currently not set as of 12-23
                limits.get("cpu", {}).get("value"),
                cpu_usage["mean"],
                cpu_usage["median"],
                cpu_usage["max"],
                cpu_usage["min"],
                cpu_usage["stddev"],
                requests["memory"]["value"],
                limits["memory"]["value"],
                mem_usage["mean"],
                mem_usage["median"],
                mem_usage["max"],
                mem_usage["min"],
                mem_usage["stddev"],
            ),
        )
    )

    # vm and build will get saved at the same time to make sure
    # we don't accidentally commit a vm without a build
    await db.commit()

    return


async def fetch_vm(hostname: str, query_time: float, db) -> dict:
    prometheus = PrometheusClient()
    vm_info = await prometheus.query(
        type="single",
        query={
            "metric": "kube_node_info",
            "filters": {"node": hostname},
        },
        time=query_time,
    )

    vm_uuid = vm_info[0]["labels"]["system_uuid"]

    async with db.execute("select id from vms where uuid = ?", (vm_uuid,)) as cursor:
        old_vm = await cursor.fetchone()

        if old_vm:
            logging.info(f"vm {hostname} already in database with id {old_vm[0]}")
            return old_vm[0]

    vm_labels = await prometheus.query(
        type="single",
        query={
            "metric": "kube_node_labels",
            "filters": {"node": hostname},
        },
        time=query_time,
    )

    async with db.execute(
        *db_insert(
            "vms",
            (
                None,
                vm_uuid,
                hostname,
                float(vm_labels[0]["labels"]["label_karpenter_k8s_aws_instance_cpu"]),
                float(
                    vm_labels[0]["labels"]["label_karpenter_k8s_aws_instance_memory"]
                ),
                vm_labels[0]["labels"]["label_kubernetes_io_arch"],
                vm_labels[0]["labels"]["label_kubernetes_io_os"],
                vm_labels[0]["labels"]["label_node_kubernetes_io_instance_type"],
            ),
        )
    ) as cursor:
        vm_id = cursor.lastrowid

    return vm_id


def is_ghost(log):
    return "No need to rebuild" in log


def process_resources_res(res: dict) -> dict:
    processed = {}
    for item in res:
        # duplicates are ignored by overwriting the previous entry
        processed[item["labels"]["resource"]] = {
            "unit": item["labels"]["unit"],
            "value": float(item["values"][1]),
        }

    return processed


def process_usage(res: dict, job_id: int) -> dict:
    if not res:
        # sometimes prometheus reports no data for a job if the time range is too small
        logging.error(f"lack of usage data for job {job_id}")
        raise InvalidDataError

    usage = [float(value) for timestamp, value in res[0]["values"]]

    sum_stats = {
        "mean": statistics.fmean(usage),
        # pstdev because we have the whole population
        "stddev": statistics.pstdev(usage),
        "max": max(usage),
        "min": min(usage),
        "median": statistics.median(usage),
    }

    if (
        sum_stats["stddev"] == 0
        or sum_stats["mean"] == 0
        or math.isnan(sum_stats["stddev"])
    ):
        logging.error(f"usage data is invalid for job {job_id}")
        raise InvalidDataError

    return sum_stats
