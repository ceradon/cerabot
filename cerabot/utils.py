def flatten(nested):
    """Combines a bunch of lists and/or tuples into one list."""
    unified_list = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            unified_list.extend(flatten(item))
        else:
            unified_list.append(x)
    return unified_list
