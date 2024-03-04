import logging

import aiosqlite

from gantry.db.get import get_node

logger = logging.getLogger(__name__)


def insert_dict(table: str, input: dict, ignore=False) -> tuple[str, tuple]:
    """
    crafts an sqlite insert statement from a dictionary.

    args:
        table: name of the table to insert into
        input: dictionary of values to insert
        ignore: whether to ignore duplicate entries

    returns: tuple of (query, values)
    """

    columns = ", ".join(input.keys())
    values = ", ".join(["?" for _ in range(len(input))])
    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

    if ignore:
        query = query.replace("INSERT", "INSERT OR IGNORE")

    # using a tuple of values from the dictionary
    values_tuple = tuple(input.values())
    return query, values_tuple


async def insert_node(db: aiosqlite.Connection, node: dict) -> int:
    """Inserts a node into the database."""

    async with db.execute(
        *insert_dict(
            "nodes",
            node,
            # deal with races
            # this also ignores the not-null constraint
            # so we need to make sure the node is valid before inserting
            ignore=True,
        )
    ) as cursor:
        # this check ensures that something was inserted
        # and not relying on lastrowid, which could be anything
        if cursor.rowcount > 0:
            return cursor.lastrowid

    pk = await get_node(db, node["uuid"])

    if pk is None:
        logger.error(f"node not inserted: {node}. data is likely missing")

    return pk


async def insert_job(db: aiosqlite.Connection, job: dict) -> int:
    """Inserts a job into the database."""

    async with db.execute(
        *insert_dict(
            "jobs",
            job,
            # if the job somehow gets added into the db (pod+id being unique)
            # then ignore the insert
            ignore=True,
        )
    ) as cursor:
        if cursor.rowcount > 0:
            return cursor.lastrowid

    logger.error(f"job not inserted: {job}. data is likely missing")
    return None
