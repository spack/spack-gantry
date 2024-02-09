import asyncio
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


async def main():
    app = web.Application()
    app.add_routes(routes)
    app.cleanup_ctx.append(init_db)
    app.on_startup.append(init_clients)
    runner = web.AppRunner(
        app, max_line_size=int(os.environ.get("MAX_GET_SIZE", 800_000))
    )
    await runner.setup()
    port = os.environ.get("GANTRY_PORT", 8080)
    host = os.environ.get("GANTRY_HOST", "localhost")
    site = web.TCPSite(
        runner,
        host,
        port,
    )
    await site.start()

    print(f"Gantry running on {host}:{port}")
    print("-------------------")

    try:
        # wait for finish signal
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
