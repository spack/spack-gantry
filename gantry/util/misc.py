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


def insert_dict(table: str, input: dict, ignore=False) -> tuple[str, tuple]:
    """
    Crafts an SQLite INSERT statement from a dictionary.

    args:
        table: name of the table to insert into
        input: dictionary of values to insert
        ignore: whether to ignore duplicate entries

    returns: tuple of (query, values)
    """

    columns = ", ".join(input.keys())
    values = ", ".join(["?" for _ in range(len(input))])
    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

    if ignore:
        query = query.replace("INSERT", "INSERT OR IGNORE")

    # using a tuple of values from the dictionary
    values_tuple = tuple(input.values())
    return query, values_tuple


def setattrs(_self, **kwargs):
    """Sets multiple attributes of an object from a dictionary."""
    for k, v in kwargs.items():
        setattr(_self, k, v)
