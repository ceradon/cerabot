from os import path, listdir

def flatten(nested):
    """Combines a bunch of lists and/or tuples into one list."""
    unified_list = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            unified_list.extend(flatten(item))
        else:
            unified_list.append(x)
    return unified_list

def list_all_files(directory, skip):
    files = []
    dir = [i for i in listdir(directory) if not i.startswith(".")]
    for name in dir:
        if path.isdir(path.join(directory, name)):
            files.extend(list_all_files(path.join(directory, name)))
        else:
            files.append(name)
    return files
