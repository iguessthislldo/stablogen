import os
import itertools 

def editor(filepath):
    os.system('%s %s' % (os.getenv('EDITOR', 'vi'), filepath))

def temp_editor(init_message=""):
    '''
    Open temporary file in program defined by EDITOR enviromental
    variable (defaults to "vi"), once the program is done, return the file
    as a string.
    '''
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / 'post'
        with tmp_file.open('w') as f:
            f.write(init_message)

        editor(str(tmp_file))

        with tmp_file.open('r') as f:
            result = f.read()

    return result

def if_none_else_do(val, func):
    ''' Return None if value is none, else return func(val) '''
    return None if val is None else func(val)

def make_url(title, url = None):
    if url is None:
        return title.lower().replace(' ', '_')
    else:
        return url

def to_list(val: str):
    return list(map(str.strip, val.split(',')))

def has_method(obj, method_name):
    return hasattr(obj, method_name) and callable(getattr(obj, method_name))

def is_empty(obj):
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

