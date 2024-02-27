from gantry.util.spec import spec_variants


def validate_payload(payload: dict) -> bool:
    """Ensures that the payload from the client is valid."""

    if not (
        # item must be dict
        isinstance(payload, dict)
        # must contain hash field
        and isinstance(payload.get("hash"), str)
        # must contain name and version
        # for both package and compiler
        and all(
            isinstance(payload.get(field, {}).get(key), str)
            for field in ["package", "compiler"]
            for key in ["name", "version"]
        )
        # look for variants inside package
        and isinstance(payload.get("package", {}).get("variants"), str)
        and spec_variants(payload["package"]["variants"]) != {}
    ):
        return False

    return True
