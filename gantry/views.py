import os
import json

from aiohttp import web

from gantry.collection import fetch_build

routes = web.RouteTableDef()


@routes.post("/collect")
async def collect_job(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400, text="invalid json")

    if request.headers.get("X-Gitlab-Token") != os.environ["GITLAB_WEBHOOK_TOKEN"]:
        return web.Response(status=401, text="invalid token")

    if request.headers.get("X-Gitlab-Event") != "Job Hook":
        return web.Response(status=400, text="invalid event type")

    await fetch_build(payload, request.app["db"])
    return web.Response(status=200)
