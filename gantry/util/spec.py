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

def valid_build_name(name):
    """Returns True if the job is a build job, False otherwise."""

    # example: plumed@2.9.0 /i4u7p6u %gcc@11.4.0
    # arch=linux-ubuntu20.04-neoverse_v1 E4S ARM Neoverse V1
    job_name_pattern = re.compile(
        r"([^/ ]+)@([^/ ]+) /([^%]+) %([^ ]+) ([^ ]+) (.+)"
    )
    job_name_match = job_name_pattern.match(name)
    # groups: 1: name, 2: version, 3: hash, 4: compiler, 5: arch, 6: stack
    return bool(job_name_match)



