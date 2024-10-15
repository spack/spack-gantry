# REST API Documentation

This section documents the behavior of Gantry's REST API, which is hosted at `https://gantry.spack.io/v1/`.

## Collection

```
POST /collect
```

This endpoint is intended to handle webhooks triggered by changes in Gitlab job status.

If the `X-Gitlab-Token` header does not match the token set in the Gitlab interface, the API will respond with `401 Unauthorized` and could lead to the webhook being disabled.

If the `X-Gitlab-Event` header does not equal "Job Hook," the response will be `200 OK`, but the client will be warned that this is an inappropriate use of the endpoint.

The payload should be include the following fields at a minimum (Gitlab will include more):

```
{
    "build_status": str,
    "build_stage": str,
    "build_id": int,
    "build_started_at": str,
    "build_finished_at": str,
    "ref": str,
    "runner": {
        "description": str
    }
}
```

The API will respond with `400 Bad Request` if any of this information is missing. Barring any other immediate issues, a background job will be queued to process the job and `200 OK` will be sent. This behavior means that there is no immediate feedback about the success of the collection; any failure is visible in the application logs. This is done to ensure that the API responds to the webhook in time and to reflect that a collection failure is not considered fatal.

## Allocation

```
GET /allocation?spec=
```

Given a spec, the API will calculate the optimal resource allocation for the job.

The spec sent to the endpoint should have the following format:

```
pkg_name@pkg_version +variant1+variant2 arch=arch%compiler@compiler_version
```

Be sure that the string is URL-encoded. For instance, the `urllib.parse.quote` method will ensure the proper format. Without it, the allocation algorithm may return inaccurate results.

**There must be a space after the package version in order to account for variant parsing.** 

If the request does not contain a valid spec, the API will respond with `400 Bad Request`. The maximum allowed size of the `GET` request is 8190 bytes.

Expected response:

```
200 OK

{
    "variables": {
        "KUBERNETES_CPU_REQUEST": str,
        "KUBERNETES_MEMORY_REQUEST": str
    }
}
```

All CPU variables will be sent in core format (e.g., "1" for 1 core), and all memory variables will be represented in megabytes (e.g., "2000M" for 2000 megabytes).

The API may change in the future to expand the number of variables, so clients should apply all values within `variables` to the job's environment.
