from aiohttp import web
from utils.collect import fetch_job

routes = web.RouteTableDef()


@routes.post("/collect")
async def collect_job(request: web.Request) -> web.Response:
    payload = await request.json()

    # TODO validate gitlab token
    if request.headers.get("X-Gitlab-Event") != "Job Hook":
        return web.Response(status=400, text="invalid event type")

    await fetch_job(payload, request.app["db"])
    return web.Response(status=200)
