import asyncio
import json
import logging
import os

from aiohttp import web

from gantry.routes.collection import fetch_job
from gantry.routes.prediction.prediction import predict_single
from gantry.util.prediction import validate_payload

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
async def allocation(request: web.Request) -> web.Response:
    """
    Given a spec in JSON format, return environment variables
    that set resource allocations based on historical data.

    acceptable payload:

    {
        "package": {
            "name": "string",
            "version": "string"
            "variants": "string"
        },
        "compiler": {
            "name": "string",
            "version": "string"
        }
    }

    returns:

    {
        "variables": {}
    }

    the variables key contains the environment variables
    that should be set within the build environment
    example: KUBERNETES_CPU_REQUEST, KUBERNETES_CPU_LIMIT, etc.
    """
    payload = request.query.get("query")

    if not payload:
        return web.Response(status=400, text="missing query parameter")

    try:
        payload = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return web.Response(status=400, text="invalid json")

    if not validate_payload(payload):
        return web.Response(status=400, text="invalid payload")

    return web.json_response(await predict_single(request.app["db"], payload))
