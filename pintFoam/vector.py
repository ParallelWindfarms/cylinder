## ------ language="Python" file="pintFoam/vector.py"
from __future__ import annotations

import numpy as np
import operator

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from shutil import copytree, rmtree

from .utils import pushd

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.UtilityRunner import UtilityRunner

## ------ begin <<base-case>>[0]
@dataclass
class BaseCase:
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
        return Vector(self, new_case, "0")

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
@dataclass
class Vector:
    base: BaseCase
    case: str
    time: str

    ## ------ begin <<pintfoam-vector-properties>>[0]
    @property
    def path(self):
        return self.base.root / self.case

    @property
    def files(self):
        return time_directory(self).getFiles()

    def internalField(self, key):
        return time_directory(self)[key] \
            .getContent()['internalField']
    ## ------ end
    ## ------ begin <<pintfoam-vector-clone>>[0]
    def clone(self):
        x = self.base.new_vector()
        x.time = self.time
        rmtree(x.path/ x.time, ignore_errors=True)
        copytree(self.path / self.time, x.path / x.time)
        return x
    ## ------ end
    ## ------ begin <<pintfoam-vector-operate>>[0]
    def _operate_vec_vec(self, other: Vector, op):
        for f in self.files:
            a_f = self.internalField(f)
            b_f = other.internalField(f)

            if a_f.uniform and b_f.uniform:
                x = self.clone()
                x_content = time_directory(x)[f].getContent()
                x_content['internalField'].val = op(a_f.val, b_f.val)
            elif a_f.uniform:
                x = other.clone()
                x_content = time_directory(x)[f].getContent()
                x_content['internalField'].val[:] = op(np.array(a_f.val), np.array(b_f.val))
            else:
                x = self.clone()
                x_content = time_directory(x)[f].getContent()
                x_content['internalField'].val[:] = op(np.array(a_f.val), np.array(b_f.val))

            x_content.writeFile()

        return x

    def _operate_vec_scalar(self, s: float, op):
        x = self.clone()
        for f in self.files:
            x_f = self.internalField(f)
            x_content = time_directory(x)[f].getContent()
            if x_f.shape is ():
                x_content['internalField'].val = op(x_f, s)
            else:
                x_content['internalField'].val[:] = op(x_f, s)
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
