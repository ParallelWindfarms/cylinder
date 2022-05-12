# ~\~ language=Python filename=pintFoam/utils.py
# ~\~ begin <<lit/cylinder.md|pintFoam/utils.py>>[0]
# ~\~ begin <<lit/cylinder.md|push-dir>>[0]
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Union
import functools
from math import (floor, log10)


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
# ~\~ begin <<lit/cylinder.md|job-names>>[0]
def generate_job_name(n, t_0, t_1, uid, id, tlength=4):
    """ Auxiliary function to generate a job name."""

    def integrify(t, length=tlength):
        """ Auxiliary function for converting a float into an integer. """
        if t==0:
            return 0
        else:
            aux = t * 10 ** -floor(log10(t)) # Remove trailing zeros
            aux = aux * 10 ** (length - 1) # Displace the decimal point to the right
        return int(aux)

    def stringify(t, length=tlength):
        if integrify(t) == 0:
            return "0" * length
        else:
            return str(integrify(t))

    return f"{n}-{stringify(t_0)}-{stringify(t_1)}-{id}-{uid.hex}"
# ~\~ end
# ~\~ end
