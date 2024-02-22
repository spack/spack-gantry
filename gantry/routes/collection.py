import logging

import aiosqlite

from gantry import db
from gantry.clients.gitlab import GitlabClient
from gantry.clients.prometheus import PrometheusClient
from gantry.clients.prometheus.util import IncompleteData
from gantry.models import Job

MB_IN_BYTES = 1_000_000

logger = logging.getLogger(__name__)


async def fetch_job(
    payload: dict,
    db_conn: aiosqlite.Connection,
    gitlab: GitlabClient,
    prometheus: PrometheusClient,
) -> None:
    """
    Fetches a job's information from Prometheus and inserts it into the database.
    If there is data missing at any point, the function will still return so the webhook
    responds as expected. If an exception is thrown, that behavior was unanticipated by
    this program and should be investigated.

    args:
        payload: a dictionary containing the information from the Gitlab job hook
        db: an active aiosqlite connection

    returns: None in order to accommodate a 200 response for the webhook.
    """

    job = Job(
        status=payload["build_status"],
        name=payload["build_name"],
        gl_id=payload["build_id"],
        start=payload["build_started_at"],
        end=payload["build_finished_at"],
        ref=payload["ref"],
    )

    # perform checks to see if we should collect data for this job
    if (
        job.status != "success"
        or not job.valid_build_name  # is not a build job
        # uo runners are not in Prometheus
        or payload["runner"]["description"].startswith("uo")
        or await db.job_exists(db_conn, job.gl_id)  # job already in the database
    ):
        return

    # check if the job is a ghost
    job_log = await gitlab.job_log(job.gl_id)
    is_ghost = "No need to rebuild" in job_log
    if is_ghost:
        logging.warning(f"job {job.gl_id} is a ghost, skipping")
        return

    try:
        annotations = await prometheus.job.get_annotations(job.gl_id, job.midpoint)
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
            **annotations,
            **resources,
            **usage,
        },
    )

    # job and node will get saved at the same time to make sure
    # we don't accidentally commit a node without a job
    await db_conn.commit()

    return job_id


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
