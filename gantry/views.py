import asyncio
import json
import logging
import os

from aiohttp import web

from gantry.routes.collection import fetch_job
from gantry.routes.prediction.prediction import predict_bulk, predict_single

logger = logging.getLogger(__name__)
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
        logger.error(f"invalid event type {request.headers.get('X-Gitlab-Event')}")
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


@routes.get("/v1/allocation")
async def allocate(request: web.Request) -> web.Response:
    """
    acceptable payload:

    {
        "hash": "string",
        "package": {
            "name": "string",
            "version": "string"
        },
        "compiler": {
            "name": "string",
            "version": "string"
        }
    }

    also accepts a list of the above objects

    returns:

    {
        "hash": "string",
        "variables": {
            "cpu_request": "float",
            "mem_request": "float",
        }
    }

    or a list of the above objects

    """

    try:
        payload = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400, text="invalid json")

    def validate_payload(payload):
        """ensures that the payload is valid"""
        if not isinstance(payload, list):
            payload = [payload]

        for item in payload:
            if not isinstance(item.get("hash"), str):
                return False

            required_fields = ["package", "compiler"]
            for field in required_fields:
                if not isinstance(item.get(field), dict):
                    return False

            if not all(
                isinstance(item.get("package", {}).get(key), str)
                for key in ["name", "version"]
            ):
                return False

            if not all(
                isinstance(item.get("compiler", {}).get(key), str)
                for key in ["name", "version"]
            ):
                return False

        return True

    if not validate_payload(payload):
        return web.Response(status=400, text="invalid payload")

    if isinstance(payload, dict):
        response = await predict_single(request.app["db"], payload)
    else:
        response = await predict_bulk(request.app["db"], payload)

    return web.json_response(response)
