def spec_variants(spec: str) -> dict:
    """Given a spec's concrete variants, return a dict in name: value format."""
    # example: +adios2~advanced_debug patches=02253c7,acb3805,b724e6a use_vtkm=on

    variants = {}
    # give some padding to + and ~ so we can split on them
    spec = spec.replace("+", " +")
    spec = spec.replace("~", " ~")
    parts = spec.split(" ")

    for part in parts:
        if len(part) < 2:
            continue
        if "=" in part:
            name, value = part.split("=")
            if "," in value:
                # array of the multiple values
                variants[name] = value.split(",")
            else:
                # string of the single value
                variants[name] = value
        else:
            # anything after the first character is the value
            if part.startswith("+"):
                variants[part[1:]] = True
            elif part.startswith("~"):
                variants[part[1:]] = False

    return variants
