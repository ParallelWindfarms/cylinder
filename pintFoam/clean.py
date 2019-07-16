## ------ language="Python" file="pintFoam/clean.py"
import sys
from pathlib import Path
from .vector import BaseCase

if __name__ == "__main__":
    target = sys.argv[1]
    base_case = sys.argv[2]
    BaseCase(Path(target), base_case).clean()
## ------ end
