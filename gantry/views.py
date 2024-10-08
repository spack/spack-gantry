import asyncio
import json
import logging
import os

from aiohttp import web

from gantry.routes.collection import fetch_job
from gantry.routes.prediction.prediction import predict
from gantry.util.spec import parse_alloc_spec

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
    Given a spec return environment variables
    that set resource allocations based on historical data.

    acceptable spec format:
    pkg_name@pkg_version +variant1+variant2%compiler@compiler_version
    NOTE: there must be a space between the package version and the variants

    returns:

    {
        "variables": {}
    }

    the variables key contains the environment variables
    that should be set within the build environment
    example: KUBERNETES_CPU_REQUEST, KUBERNETES_CPU_LIMIT, etc.
    """
    spec = request.query.get("spec")

    if not spec:
        return web.Response(status=400, text="missing spec parameter")

    parsed_spec = parse_alloc_spec(spec)
    if not parsed_spec:
        return web.Response(status=400, text="invalid spec")

    return web.json_response(await predict(request.app["db"], parsed_spec))
