def spec_variants(spec: str) -> dict:
    """Given a spec's concrete variants, return a dict of variant name: value."""
    # example: +adios2~advanced_debug patches=02253c7,acb3805,b724e6a use_vtkm=on

    # TODO handle errors and invalid inputs

    variants = {}
    spec = spec.replace("+", " +")
    spec = spec.replace("~", " ~")
    parts = spec.split(" ")

    for part in parts:
        if "=" in part:
            name, value = part.split("=")
            # multiple values
            if "," in value:
                variants[name] = value.split(",")
            else:
                variants[name] = value
        else:
            if part.startswith("+"):
                variants[part[1:]] = True
            elif part.startswith("~"):
                variants[part[1:]] = False

    return variants
