# ~\~ language=Python filename=pintFoam/utils.py
# ~\~ begin <<lit/cylinder.md|pintFoam/utils.py>>[0]
# ~\~ begin <<lit/cylinder.md|push-dir>>[0]
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Union

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
