# fixtures shared among all tests

import aiosqlite
import pytest


@pytest.fixture
async def db_conn():
    """
    In-memory sqlite connection ensures that the database is clean for each test
    """
    db = await aiosqlite.connect(":memory:")
    with open("db/schema.sql") as f:
        await db.executescript(f.read())
    yield db
    await db.close()
