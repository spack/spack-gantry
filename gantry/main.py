import os

import aiosqlite
from aiohttp import web
from views import routes


async def init_db(app: web.Application):
    db = await aiosqlite.connect(os.environ["DB_FILE"])
    await db.execute("PRAGMA foreign_keys = ON;")
    app["db"] = db
    yield
    await db.close()


app = web.Application()
app.add_routes(routes)
app.cleanup_ctx.append(init_db)
web.run_app(app)
