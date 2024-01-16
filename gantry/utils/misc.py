def spec_variants(spec: str) -> dict:
    """Given a spec's concrete variants, return a dict of name: value."""
    # example: +adios2~advanced_debug patches=02253c7,acb3805,b724e6a use_vtkm=on

    variants = {}
    spec = spec.replace("+", " +")
    spec = spec.replace("~", " ~")
    parts = spec.split(" ")

    for part in parts:
        if len(part) < 2:
            continue
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


def db_insert(table, values):
    """
    Returns an INSERT statement given a table name and tuple of values.
    Must provide values for all columns in the table, including the primary key.
    """
    return (
        f"insert into {table} values ({','.join(['?'] * (len(values)) )})",
        values,
    )
