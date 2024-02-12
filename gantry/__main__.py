import os

import aiosqlite
from aiohttp import web

from gantry.clients.gitlab import GitlabClient
from gantry.clients.prometheus import PrometheusClient
from gantry.views import routes


async def init_db(app: web.Application):
    db = await aiosqlite.connect(os.environ["DB_FILE"])
    await db.execute("PRAGMA foreign_keys = ON;")
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
