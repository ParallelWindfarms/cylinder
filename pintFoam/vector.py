## ------ language="Python" file="pintFoam/vector.py"
import numpy as np
import operator

from typing import NamedTuple
from pathlib import Path
from uuid import uuid4
from shutil import copytree, rmtree

from .utils import pushd

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.UtilityRunner import UtilityRunner

## ------ begin <<base-case>>[0]
class BaseCase(NamedTuple):
    """Base case is a cleaned version of the system. If it contains any fields,
    it will only be the `0` time. Any field that is copied for manipulation will
    do so on top of an available base case in the `0` slot."""
    root: Path
    case: str

    @property
    def path(self):
        return self.root / self.case

    def new_vector(self, name=None):
        """Creates new `Vector` using this base case."""
        new_case = name or uuid4().hex
        new_path = self.root / new_case
        if not new_path.exists():
            copytree(self.path, new_path)
        return Vector(self, new_case, 0)

    def all_vector_paths(self):
        """Iterates all sub-directories in the root."""
        return (x for x in self.root.iterdir()
                if x.is_dir() and x.name != self.case)

    def clean(self):
        """Deletes all vectors of this base-case."""
        for path in self.all_vector_paths():
            rmtree(path)
## ------ end
## ------ begin <<pintfoam-vector>>[0]
def solution_directory(case):
    return SolutionDirectory(case.path)


def parameter_file(case, relative_path):
    return ParsedParameterFile(case.path / relative_path)


def time_directory(case):
    return solution_directory(case)[case.time]
## ------ end
## ------ begin <<pintfoam-vector>>[1]
class Vector(NamedTuple):
    base: BaseCase
    case: str
    time: int

    ## ------ begin <<pintfoam-vector-properties>>[0]
    @property
    def path(self):
        return self.base.root / self.case
    
    @property
    def files(self):
        return time_directory(self).getFiles()    
    
    def internalField(self, key):
        return np.array(time_directory(self)[key] \
            .getContent().content['internalField'])
    ## ------ end
    ## ------ begin <<pintfoam-vector-operate>>[0]
    def _operate_vec_vec(self, other: Vector, op):
        x = self.base.new_vector()
        for f in self.files:
            a_f = self.internalField(f)
            b_f = other.internalField(f)
            x_content = time_directory(x)[f].getContent()
            x_f = x_content.content['internalField'].val[:] = op(a_f, b_f)
            x_content.writeFile()
        return x
    
    def _operate_vec_scalar(self, s: float, op):
        x = self.base.new_vector()
        for f in self.files:
            a_f = self.internalField(f)
            x_content = time_directory(x)[f].getContent()
            x_f = x_content.content['internalField'].val[:] = op(a_f, s)
            x_content.writeFile()
        return x        
    ## ------ end
    ## ------ begin <<pintfoam-vector-operators>>[0]
    def __sub__(self, other: Vector):
        return self._operate_vec_vec(other, operator.sub)
    
    def __add__(self, other: Vector):
        return self._operate_vec_vec(other, operator.add)
    
    def __mul__(self, scale: float):
        return self._operate_vec_scalar(scale, operator.mul)
    ## ------ end
## ------ end
## ------ begin <<pintfoam-set-fields>>[0]
def setFields(v, *, defaultFieldValues, regions):
    x = parameter_file(v, "system/setFieldsDict")
    x['defaultFieldValues'] = defaultFieldValues
    x['regions'] = regions
    x.writeFile()

    with pushd(v.path):
        u = UtilityRunner(argv=['setFields'], silent=True)
        u.start()
## ------ end
## ------ end
