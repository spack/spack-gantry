import pytest

from gantry.clients.gitlab import GitlabClient
from gantry.clients.prometheus import PrometheusClient
from gantry.routes.collection import fetch_job, fetch_node, handle_pipeline
from gantry.tests.defs import collection as defs

# mapping of prometheus request shortcuts
# to raw values that would be returned by resp.json()

# note: the ordering of this dict indicated the order of the calls.
# if the order in which PrometheusClient._query is called changes,
# this dict must be updated
PROMETHEUS_REQS = {
    "job_annotations": defs.VALID_ANNOTATIONS,
    "job_resources": defs.VALID_RESOURCE_REQUESTS,
    "job_limits": defs.VALID_RESOURCE_LIMITS,
    "job_memory_usage": defs.VALID_MEMORY_USAGE,
    "job_cpu_usage": defs.VALID_CPU_USAGE,
    "node_info": defs.VALID_NODE_INFO,
    "node_labels": defs.VALID_NODE_LABELS,
}


@pytest.fixture
async def gitlab(mocker, request):
    """Returns GitlabClient with some default (mocked) behavior"""

    # mock the request to the gitlab api
    # default is to return normal log that wouldn't be detected as a ghost job
    mocker.patch.object(GitlabClient, "_request", return_value=defs.VALID_JOB_LOG)

    # Optionally mock the start_pipeline method if needed
    if getattr(request, "param", {}).get("with_restart", False):
        mocker.patch.object(GitlabClient, "start_pipeline", return_value=None)

    return GitlabClient("", "")


@pytest.fixture
async def prometheus(mocker):
    """Returns PrometheusClient with some default (mocked) behavior"""

    # use dict value iterable to mock multiple calls
    mocker.patch.object(
        PrometheusClient, "_query", side_effect=PROMETHEUS_REQS.values()
    )
    return PrometheusClient("", "")


@pytest.mark.parametrize(
    "key, value",
    [
        ("build_status", defs.INVALID_JOB_STATUS),
        ("build_stage", defs.INVALID_STAGE),
        ("runner", defs.INVALID_RUNNER),
    ],
)
async def test_invalid_gitlab_fields(db_conn, gitlab, prometheus, key, value):
    """Tests behavior when invalid data from Gitlab is passed to fetch_job"""
    payload = defs.VALID_JOB.copy()
    payload[key] = value

    assert await fetch_job(payload, db_conn, gitlab, prometheus) is None


async def test_job_exists(db_conn):
    """
    Tests that fetch_job returns None when the job already exists in the database.
    The return value of fetch_job is only used to indicate when a job is inserted,
    not if it's found in the database.
    """
    # node must be inserted before job to avoid foreign key constraint
    with open("gantry/tests/sql/insert_node.sql") as f:
        await db_conn.executescript(f.read())
    with open("gantry/tests/sql/insert_job.sql") as f:
        await db_conn.executescript(f.read())

    assert await fetch_job(defs.VALID_JOB, db_conn, None, None) is None


async def test_ghost_job(db_conn, gitlab, mocker):
    """Tests that a ghost job is detected"""

    mocker.patch.object(gitlab, "_request", return_value=defs.GHOST_JOB_LOG)
    assert await fetch_job(defs.VALID_JOB, db_conn, gitlab, None) is None


@pytest.mark.parametrize(
    "req",
    [
        "job_annotations",
        "job_resources",
        "job_limits",
        "job_memory_usage",
        "job_cpu_usage",
        "node_info",
        "node_labels",
    ],
)
async def test_missing_data(db_conn, gitlab, prometheus, req):
    """Tests behavior when Prometheus data is missing for certain requests"""

    p = PROMETHEUS_REQS.copy()
    # for each req in PROMETHEUS_REQS, set it to an empty dict
    p[req] = {}
    prometheus._query.side_effect = p.values()
    assert await fetch_job(defs.VALID_JOB, db_conn, gitlab, prometheus) is None


async def test_invalid_usage(db_conn, gitlab, prometheus):
    """Test that when resource usage is invalid (eg mean=0), the job is not inserted"""

    p = PROMETHEUS_REQS.copy()
    # could also be cpu usage
    p["job_memory_usage"] = defs.INVALID_MEMORY_USAGE
    prometheus._query.side_effect = p.values()
    assert await fetch_job(defs.VALID_JOB, db_conn, gitlab, prometheus) is None


async def test_job_node_inserted(db_conn, gitlab, prometheus):
    """Tests that the job and node are in the database after calling fetch_node"""

    await fetch_job(defs.VALID_JOB, db_conn, gitlab, prometheus)
    # as the first records in the database, the ids should be 1
    async with db_conn.execute("SELECT * FROM jobs WHERE id=?", (1,)) as cursor:
        job = await cursor.fetchone()
    async with db_conn.execute("SELECT * FROM nodes WHERE id=?", (1,)) as cursor:
        node = await cursor.fetchone()
    assert job == defs.INSERTED_JOB
    assert node == defs.INSERTED_NODE


async def test_node_exists(db_conn, prometheus):
    """Tests that fetch_node returns the existing node id when the node
    is already in the database"""

    # when fetch_node is called, only two prometheus requests are made
    # (see comment above PROMETHEUS_REQS)
    prometheus._query.side_effect = [
        PROMETHEUS_REQS["node_info"],
        PROMETHEUS_REQS["node_labels"],
    ]

    # in the inserted row, the node id is 2 because if the fetch_node call
    # inserts a new node, the id would be set to 1
    with open("gantry/tests/sql/insert_node.sql") as f:
        await db_conn.executescript(f.read())

    assert await fetch_node(db_conn, prometheus, None, None) == 2


@pytest.mark.parametrize("gitlab", [{"with_restart": True}], indirect=True)
async def test_handle_pipeline(db_conn, gitlab, prometheus):
    """Tests the behavior of handle_pipeline with different pipeline
    and job statuses."""

    p = PROMETHEUS_REQS.copy()

    # successful pipeline
    assert (
        await handle_pipeline(defs.SUCCESSFUL_PIPELINE, db_conn, gitlab, prometheus)
        is None
    )

    # pipeline failed and not oomed
    p_list = list(p.values())
    # insert a prometheus response indicating the job was not oom killed
    p_list.insert(1, defs.NOT_OOM_KILLED)
    prometheus._query.side_effect = p_list
    assert (
        await handle_pipeline(defs.FAILED_PIPELINE, db_conn, gitlab, prometheus) is None
    )

    # pipeline failed, one job was oomed the other was not
    p_list = list(p.values())
    # after verifying job was not oomed, go onto the next job to insert annotations
    p_list[1:1] = [defs.NOT_OOM_KILLED, p["job_annotations"], defs.OOM_KILLED]
    prometheus._query.side_effect = p_list
    # duplicate the same job so it calls fetch_job twice
    pipeline = defs.FAILED_PIPELINE.copy()
    pipeline["builds"].append(pipeline["builds"][0])
    assert await handle_pipeline(pipeline, db_conn, gitlab, prometheus)

    # verify that OOM job was inserted
    async with db_conn.execute("SELECT * FROM jobs WHERE id=?", (1,)) as cursor:
        job = await cursor.fetchone()
    assert job == defs.INSERTED_OOM_JOB


# TODO test if OOM status is correct
# TODO test start_pipeline response is json not None
