import asyncio
import json
import logging
import os

from aiohttp import web

from gantry.routes.collection import fetch_job

routes = web.RouteTableDef()


@routes.post("/v1/collect")
async def collect_job(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400, text="invalid json")

    if request.headers.get("X-Gitlab-Token") != os.environ["GITLAB_WEBHOOK_TOKEN"]:
        return web.Response(status=401, text="invalid token")

    if request.headers.get("X-Gitlab-Event") != "Job Hook":
        logging.error(
            f"invalid event type {request.headers.get('X-Gitlab-Event')} received from Gitlab."
        )
        # return 200 so gitlab doesn't disable the webhook -- this is not fatal
        return web.Response(status=200)

    # will return immediately, but will not block the event loop
    # allowing fetch_job to run in the background
    asyncio.ensure_future(
        fetch_job(
            payload, request.app["db"], request.app["gitlab"], request.app["prometheus"]
        )
    )

    return web.Response(status=200)
