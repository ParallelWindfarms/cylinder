## ------ language="Python" file="pintFoam/utils.py"
## ------ begin <<push-dir>>[0]
import os
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def pushd(path):
    """Context manager to change directory to given path,
    and get back to current dir at exit."""
    prev = Path.cwd()
    os.chdir(path)
    
    try:
        yield
    finally:
        os.chdir(prev)
## ------ end
## ------ end
