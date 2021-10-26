# ~\~ language=Python filename=pintFoam/utils.py
# ~\~ begin <<lit/cylinder.md|pintFoam/utils.py>>[0]
# ~\~ begin <<lit/cylinder.md|push-dir>>[0]
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Union
import functools


def decorator(f):
    """Creates a parametric decorator from a function. The resulting decorator
    will optionally take keyword arguments."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if args and len(args) == 1:
            return f(*args, **kwargs)

        if args:
            raise TypeError(
                "This decorator only accepts extra keyword arguments.")

        return lambda g: f(g, **kwargs)

    return decorated_function


@contextmanager
def pushd(path: Union[str, Path]):
    """Context manager to change directory to given path,
    and get back to current dir at exit."""
    prev = Path.cwd()
    os.chdir(path)

    try:
        yield
    finally:
        os.chdir(prev)
# ~\~ end
# ~\~ end
