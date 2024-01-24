def setattrs(_self, **kwargs):
    """Sets multiple attributes of an object from a dictionary."""
    for k, v in kwargs.items():
        setattr(_self, k, v)
