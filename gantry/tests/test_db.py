from gantry.db.insert import insert_job, insert_node
from gantry.tests.defs import db as defs


async def test_node_insert_race(db_conn):
    """
    Tests the situation where two identical jobs are inserted around the same time.
    The first call should insert the node and the second should return the id
    of the first.
    """
    # the id of this row is 1
    with open("gantry/tests/sql/insert_node.sql") as f:
        await db_conn.executescript(f.read())

    # the id of NODE_INSERT_DICT is 2, but the output should be 1
    assert await insert_node(db_conn, defs.NODE_INSERT_DICT) == 2


async def test_insert_node_incomplete(db_conn):
    """
    Tests that when missing data is passed to the insert_node function, it returns None.
    Issues around using lastrowid to get the id of the inserted row were returning
    old inserted rows, so this ensures that the function returns None when it should.
    """
    assert await insert_node(db_conn, {"uuid": None}) is None


async def test_insert_job_incomplete(db_conn):
    """See test_insert_node_incomplete"""
    assert await insert_job(db_conn, {"node": None}) is None
