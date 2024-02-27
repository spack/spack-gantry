from gantry.util.spec import spec_variants


def validate_payload(payload: dict) -> bool:
    """Ensures that the payload from the client is valid."""
    # must be a dict or a list
    if not isinstance(payload, (dict, list)):
        return False

    if isinstance(payload, dict):
        # put dict in list for iteration
        payload = [payload]

    for item in payload:
        if not (
            # item must be dict
            isinstance(item, dict)
            # must contain hash field
            and isinstance(item.get("hash"), str)
            # must contain name and version
            # for both package and compiler
            and all(
                isinstance(item.get(field, {}).get(key), str)
                for field in ["package", "compiler"]
                for key in ["name", "version"]
            )
            # look for variants inside package
            and isinstance(item.get("package", {}).get("variants"), str)
            and spec_variants(item["package"]["variants"]) != {}
        ):
            return False

    return True
