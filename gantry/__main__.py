import logging
import os

import aiosqlite
from aiohttp import web

from gantry.clients.gitlab import GitlabClient
from gantry.clients.prometheus import PrometheusClient
from gantry.views import routes

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "WARNING"),
    format="[%(asctime)s] (%(name)s:%(lineno)d) %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def apply_migrations(db: aiosqlite.Connection):
    # grab the current version of the database
    async with db.execute("PRAGMA user_version") as cursor:
        row = await cursor.fetchone()
        current_version = row[0]

    migrations = [
        # migrations manually defined here to ensure
        # they are applied in the correct order
        # and not inadvertently added to the migrations folder
        ("001_initial.sql", 1),
    ]

    # apply migrations that have not been applied
    # by comparing the current version to the version of the migration
    for migration, version in migrations:
        if current_version < version:
            logger.info(f"Applying migration {migration}")
            with open(f"migrations/{migration}") as f:
                await db.executescript(f.read())
            # update the version of the database
            await db.execute(f"PRAGMA user_version = {version}")
            await db.commit()


async def init_db(app: web.Application):
    db = await aiosqlite.connect(os.environ["DB_FILE"])
    await apply_migrations(db)
    app["db"] = db
    yield
    await db.close()


async def init_clients(app: web.Application):
    app["gitlab"] = GitlabClient(
        os.environ["GITLAB_URL"], os.environ["GITLAB_API_TOKEN"]
    )
    app["prometheus"] = PrometheusClient(
        os.environ["PROMETHEUS_URL"], os.environ.get("PROMETHEUS_COOKIE", "")
    )


def main():
    app = web.Application()
    app.add_routes(routes)
    app.cleanup_ctx.append(init_db)
    app.on_startup.append(init_clients)
    web.run_app(app)


if __name__ == "__main__":
    main()
