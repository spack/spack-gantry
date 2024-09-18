import asyncio
import json
import logging
import os

from aiohttp import web

from gantry.routes.collection import fetch_job, handle_pipeline
from gantry.routes.prediction.prediction import predict
from gantry.util.spec import parse_alloc_spec

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.post("/v1/collect")
async def collect(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400, text="invalid json")

    if request.headers.get("X-Gitlab-Token") != os.environ["GITLAB_WEBHOOK_TOKEN"]:
        return web.Response(status=401, text="invalid token")

    hook_type = request.headers.get("X-Gitlab-Event")
    job_args = (
        payload,
        request.app["db"],
        request.app["gitlab"],
        request.app["prometheus"],
    )
    if hook_type == "Job Hook":
        # using ensure_future because it doesn't block the event loop
        # and returns immediately, allowing jobs to run in the background
        asyncio.ensure_future(fetch_job(*job_args))
    elif hook_type == "Pipeline Hook":
        asyncio.ensure_future(handle_pipeline(*job_args))
    else:
        # this is not fatal, but we should log it
        logger.error(f"invalid event type {hook_type}")

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

    # we want to keep predictions >= current levels (with ensure_higher strategy)
    return web.json_response(
        await predict(request.app["db"], parsed_spec, strategy="ensure_higher")
    )
