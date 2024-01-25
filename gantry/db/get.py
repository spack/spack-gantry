import logging

import aiosqlite


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
            logging.warning(
                f"""
                job {gl_id} already in database.
                check why multiple requests are being sent.
                """
            )
            return True

    return False


async def ghost_exists(db: aiosqlite.Connection, gl_id: int) -> bool:
    """return if the ghost job exists in the database"""

    async with db.execute(
        "select id from ghost_jobs where gitlab_id = ?", (gl_id,)
    ) as cursor:
        if await cursor.fetchone():
            return True

    return False
