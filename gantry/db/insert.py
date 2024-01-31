import aiosqlite

from gantry.db.get import get_node


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
            ignore=True,
        )
    ) as cursor:
        pk = cursor.lastrowid

    if pk == 0:
        # the ignore part of the query was triggered, some other call
        # must have inserted the node before this one
        pk = await get_node(db, node["uuid"])

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
        return cursor.lastrowid
