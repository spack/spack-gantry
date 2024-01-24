import logging

import aiosqlite

from gantry.models import VM, Build
from gantry.clients.gitlab import GitlabClient
from gantry.clients.prometheus import IncompleteData, PrometheusClient


async def fetch_build(
    payload: dict,
    db: aiosqlite.Connection,
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

    returns: None in order to accomodate a 200 response for the webhook.
    """

    build = Build(
        status=payload["build_status"],
        name=payload["build_name"],
        id=payload["build_id"],
        start=payload["build_started_at"],
        end=payload["build_finished_at"],
        retries=payload["retries_count"],
        ref=payload["ref"],
    )

    # perform checks to see if we should collect data for this job
    if (
        build.status not in ("success",)
        or not build.valid_name  # is not a build job
        or await build.in_db(db)  # job already in the database
        or await build.is_ghost(db, gitlab)
    ):
        return

    try:
        await build.get_annotations(prometheus)
        await build.get_resources(prometheus)
        await build.get_usage(prometheus)
        vm_id = await fetch_vm(db, prometheus, build.node, build.midpoint)
    except IncompleteData as e:
        # missing data, skip this job
        logging.error(e)
        return

    await build.insert(db, vm_id)
    # vm and build will get saved at the same time to make sure
    # we don't accidentally commit a vm without a build
    await db.commit()

    return


async def fetch_vm(
    db: aiosqlite.Connection,
    prometheus: PrometheusClient,
    hostname: dict,
    query_time: float,
) -> int:
    """
    Finds an existing VM in the database or inserts a new one.

    args:
        db: an active aiosqlite connection
        prometheus:
        hostname: the hostname of the VM
        query_time: any point during VM runtime, usually grabbed from build

    returns: id of the inserted or existing VM
    """
    vm = VM(
        hostname=hostname,
        query_time=query_time,
    )

    # do not proceed if the VM exists
    if existing_vm := await vm.db_id(db, prometheus):
        return existing_vm

    await vm.get_labels(prometheus)
    return await vm.insert(db)
