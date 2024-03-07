import re


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


def parse_alloc_spec(spec: str) -> dict:
    """
    Parses a spec in the format emacs@29.2 +json+native+treesitter%gcc@12.3.0
    and returns a dictionary with the following keys:
    - pkg_name: str
    - pkg_version: str
    - pkg_variants: dict
    - compiler: str
    - compiler_version: str

    Returns an empty dict if the spec is invalid.

    This format is specifically used for the allocation API and is documented
    for the client.
    """

    # example: emacs@29.2 +json+native+treesitter%gcc@12.3.0
    spec_pattern = re.compile(r"(.+?)@([\d.]+)\s+(.+?)%([\w-]+)@([\d.]+)")

    match = spec_pattern.match(spec)
    if not match:
        return {}

    # groups in order
    # create a dictionary with the keys and values
    (
        pkg_name, 
        pkg_version, 
        pkg_variants, 
        compiler_name, 
        compiler_version
    ) = match.groups()

    spec_dict = {
        "pkg_name": pkg_name,
        "pkg_version": pkg_version,
        "pkg_variants": spec_variants(pkg_variants),
        "compiler_name": compiler_name,
        "compiler_version": compiler_version,
    }

    if not spec_dict["pkg_variants"]:
        return {}

    return spec_dict
