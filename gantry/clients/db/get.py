import logging

import aiosqlite

logger = logging.getLogger(__name__)


async def get_node(db: aiosqlite.Connection, uuid: str) -> int | None:
    """return the primary key if found, otherwise return None"""

    async with db.execute("select id from nodes where uuid = ?", (uuid,)) as cursor:
        if cur_node := await cursor.fetchone():
            return cur_node[0]

    return None


async def job_exists(db: aiosqlite.Connection, gl_id: int) -> bool:
    """return if the job exists in the database"""

    async with db.execute(
        "select id from jobs where gitlab_id = ?", (gl_id,)
    ) as cursor:
        if await cursor.fetchone():
            logger.warning(f"job {gl_id} exists. look into duplicate webhook calls.")
            return True

    return False
