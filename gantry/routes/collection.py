import logging
import re

import aiosqlite

from gantry.clients import db
from gantry.clients.gitlab import GitlabClient
from gantry.clients.prometheus import PrometheusClient
from gantry.clients.prometheus.util import IncompleteData
from gantry.models import Job

MB_IN_BYTES = 1_000_000
BUILD_STAGE_REGEX = r"^stage-\d+$"

logger = logging.getLogger(__name__)


async def handle_pipeline(
    payload: dict,
    db_conn: aiosqlite.Connection,
    gitlab: GitlabClient,
    prometheus: PrometheusClient,
) -> None | bool:
    """
    Sends any failed jobs from a pipeline to fetch_job.
    If any of the failed jobs were OOM killed, the pipeline will be recreated.

    args:
        payload: a dictionary containing the information from the Gitlab pipeline hook
        db: an active aiosqlite connection
        gitlab: gitlab client
        prometheus: prometheus client

    returns: True if the pipeline was recreated, else None
    """

    if payload["object_attributes"]["status"] != "failed":
        return

    ref = payload["object_attributes"]["ref"]
    failed_jobs = [
        # imitate the payload from the job hook, which fetch_jobs expects
        {
            "build_status": job["status"],
            "build_id": job["id"],
            "build_started_at": job["started_at"],
            "build_finished_at": job["finished_at"],
            "ref": ref,
            "build_stage": job["stage"],
            "runner": job["runner"],
        }
        for job in payload["builds"]
        if job["status"] == "failed"
    ]

    retry_pipeline = False

    for job in failed_jobs:
        # insert every potentially oomed job
        oomed = await fetch_job(job, db_conn, gitlab, prometheus)
        # fetch_job can return None or (job_id: int, oomed: bool)
        if oomed and oomed[1]:
            retry_pipeline = True

    # once all jobs are collected/discarded, retry the pipeline if needed
    if retry_pipeline:
        await gitlab.start_pipeline(ref)
        print("hi")
        return True


async def fetch_job(
    payload: dict,
    db_conn: aiosqlite.Connection,
    gitlab: GitlabClient,
    prometheus: PrometheusClient,
) -> tuple[int, bool] | None:
    """
    Collects a job's information from Prometheus and inserts into db.
    Warnings about missing data will be logged; check uncaught exceptions.
    Fetches a job's information from Prometheus and inserts it into the database.

    args:
        payload: a dictionary containing the information from the gitlab job hook
        db: an active aiosqlite connection
        gitlab: gitlab client
        prometheus: prometheus client

    returns: if data was inserted,
                a tuple of the job id and if the job was OOM killed, else None
    """

    job = Job(
        status=payload["build_status"],
        gl_id=payload["build_id"],
        start=payload["build_started_at"],
        end=payload["build_finished_at"],
        ref=payload["ref"],
    )

    # perform checks to see if we should collect data for this job
    if (
        job.status not in ("success", "failed")
        # if the stage is not stage-NUMBER, it's not a build job
        or not re.match(BUILD_STAGE_REGEX, payload["build_stage"])
        # some jobs don't have runners..?
        or payload["runner"] is None
        # uo runners are not in Prometheus
        or payload["runner"]["description"].strip().startswith("uo")
        # job already in the database
        or await db.job_exists(db_conn, job.gl_id)
    ):
        return

    # check if the job is a ghost
    job_log = await gitlab.job_log(job.gl_id)
    is_ghost = "No need to rebuild" in job_log
    if is_ghost:
        logger.warning(f"job {job.gl_id} is a ghost, skipping")
        return

    # track if job was OOM killed and needs to be retried
    oomed = False

    try:
        annotations = await prometheus.job.get_annotations(job.gl_id, job.midpoint)
        # check if failed job was OOM killed,
        # return early if it wasn't because we don't care about it anymore
        if job.status == "failed":
            if await prometheus.job.is_oom(annotations["pod"], job.start, job.end):
                oomed = True
            else:
                return

        resources, node_hostname = await prometheus.job.get_resources(
            annotations["pod"], job.midpoint
        )
        usage = await prometheus.job.get_usage(annotations["pod"], job.start, job.end)
        node_id = await fetch_node(db_conn, prometheus, node_hostname, job.midpoint)
    except IncompleteData as e:
        # missing data, skip this job
        logger.error(f"{e} job={job.gl_id}")
        return

    job_id = await db.insert_job(
        db_conn,
        {
            "node": node_id,
            "start": job.start,
            "end": job.end,
            "gitlab_id": job.gl_id,
            "job_status": job.status,
            "ref": job.ref,
            "oomed": oomed,
            **annotations,
            **resources,
            **usage,
        },
    )

    # job and node will get saved at the same time to make sure
    # we don't accidentally commit a node without a job
    await db_conn.commit()
    return (job_id, oomed)


async def fetch_node(
    db_conn: aiosqlite.Connection,
    prometheus: PrometheusClient,
    hostname: dict,
    query_time: float,
) -> int:
    """
    Finds an existing node in the database or inserts a new one.

    args:
        db: an active aiosqlite connection
        prometheus:
        hostname: the hostname of the node
        query_time: any point during node runtime, usually grabbed from job

    returns: id of the inserted or existing node
    """

    node_uuid = await prometheus.node.get_uuid(hostname, query_time)

    # do not proceed if the node exists
    if existing_node := await db.get_node(db_conn, node_uuid):
        return existing_node

    node_labels = await prometheus.node.get_labels(hostname, query_time)
    return await db.insert_node(
        db_conn,
        {
            "uuid": node_uuid,
            "hostname": hostname,
            "cores": node_labels["cores"],
            # convert to bytes to be consistent with other resource metrics
            "mem": node_labels["mem"] * MB_IN_BYTES,
            "arch": node_labels["arch"],
            "os": node_labels["os"],
            "instance_type": node_labels["instance_type"],
        },
    )
