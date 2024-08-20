# fixtures shared among all tests

import aiosqlite
import pytest

from gantry.__main__ import apply_migrations


@pytest.fixture
async def db_conn():
    """
    In-memory sqlite connection ensures that the database is clean for each test
    """
    db = await aiosqlite.connect(":memory:")
    # apply the schema
    await apply_migrations(db)
    yield db
    await db.close()
