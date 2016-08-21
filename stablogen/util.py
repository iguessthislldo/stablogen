import os
import itertools 

def if_none_else_do(val, func):
    ''' Return None if value is none, else return func(val) '''
    return None if val is None else func(val)

def make_url(title, url = None):
    if url is None:
        return title.lower().replace(' ', '_')
    else:
        return url

def to_list(val: str): # Not being used?
    return list(map(str.strip, val.split(',')))

def has_method(obj, method_name):
    '''See if object has a method, should work if its assigned to class or
    to the object itself.
    '''
    return hasattr(obj, method_name) and callable(getattr(obj, method_name))

def is_empty(obj):
    '''Determines if a iter object is empty. First checks if its a generator,
    then sees if it throws StopIteration the first time. If its not a generator
    then it just checks the length.
    '''
    if not has_method(obj, "__iter__"):
        raise TypeError("obj does not have an __iter__ method")

    if has_method(obj, "__next__"):
        try:
            next(obj)
        except StopIteration:
            return True
        return False
    else:
        return len(obj) == 0

def find_files(directory, names=None, exts=None, union=True):
    # This is a GoF Pattern, but I can't remember the name (the book is out of
    # reach and I'm too lazy to Google it)
    if isinstance(names, str):
        names = (names,)
    if isinstance(exts, str):
        exts = (exts,)
    if names is not None and exts is None:
        names = tuple(names)
        f = lambda i: i.startswith(names)
    elif names is None and exts is not None:
        exts = tuple(exts)
        f = lambda i: i.endswith(exts)
    elif names is not None and exts is not None:
        names = tuple(names)
        exts = tuple(exts)
        f = (
                lambda i: i.startswith(names) or i.endswith(exts)
            ) if union else (
                lambda i: i.startswith(names) and i.endswith(exts)
            )
    else: # Both are None
        f = lambda i: True

    files = []
    for i in directory.iterdir():
        if i.is_file() and f(i.name):
            files.append(i)
    return files

def find_file(directory, names=None, exts=None):
    '''Finds a file in a given pathlib.Path directory with a name and a iter
    of extentions. If not found, return None. A wrap around find_files.
    '''
    result = find_files(directory, names, exts)
    return result[0] if result else None
