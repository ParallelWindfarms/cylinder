# ~\~ language=Python filename=pintFoam/vector.py
# ~\~ begin <<lit/cylinder.md|pintFoam/vector.py>>[0]
from __future__ import annotations

import operator
import adios2

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from shutil import copytree, rmtree, copy

# from .utils import pushd

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile  # type: ignore
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory      # type: ignore

# ~\~ begin <<lit/cylinder.md|base-case>>[0]
@dataclass
class BaseCase:
    """Base case is a cleaned version of the system. If it contains any fields,
    it will only be the `0` time. Any field that is copied for manipulation will
    do so on top of an available base case in the `0` slot."""
    root: Path
    case: str
    fields: List[str] = None

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
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-vector>>[0]
def solution_directory(case):
    return SolutionDirectory(case.path)

def parameter_file(case, relative_path):
    return ParsedParameterFile(case.path / relative_path)

def time_directory(case):
    return solution_directory(case)[case.time]
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-vector>>[1]
@dataclass
class Vector:
    base: BaseCase
    case: str
    time: str

    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-properties>>[0]
    @property
    def path(self):
        return self.base.root / self.case

    @property
    def fields(self):
        return self.base.fields

    @property
    def filename(self):
        return self.path / "adiosData" / (self.time + ".bp")

    @property
    def dirname(self):
        return self.path / "adiosData" / (self.time + ".bp.dir")

    def data(self, mode="r"):
        return adios2.open(str(self.filename), mode)
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-clone>>[0]
    def clone(self):
        x = self.base.new_vector()
        x.time = self.time
        rmtree(x.path / "adiosData", ignore_errors=True)
        (x.path / "adiosData").mkdir()
        try:
            copy(self.filename, x.path / "adiosData")
            copytree(self.dirname, x.dirname)
        except OSError as e:
            # FIXME: Warn if this happens if self.time != "0"
            print(e)
            pass
        return x
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-operate>>[0]
    def _operate_vec_vec(self, other: Vector, op) -> Vector:
        x = self.clone()
        a_data = self.data()
        b_data = other.data()
        x_data = x.data(mode="w")
        for f in self.fields:
            a_f = a_data.read(f)
            b_f = b_data.read(f)
            x_f = op(a_f, b_f)
            x_data.write(f, x_f)
        return x

    def _operate_vec_scalar(self, s: float, op) -> Vector:
        x = self.clone()
        a_data = self.data()
        x_data = x.data(mode="w")
        for f in self.fields:
            a_f = a_data.read(f)
            x_f = op(a_f, s)
            x_data.write(f, x_f)
        return x
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-operators>>[0]
    def __sub__(self, other: Vector) -> Vector:
        return self._operate_vec_vec(other, operator.sub)

    def __add__(self, other: Vector) -> Vector:
        return self._operate_vec_vec(other, operator.add)

    def __mul__(self, scale: float) -> Vector:
        return self._operate_vec_scalar(scale, operator.mul)
    # ~\~ end
# ~\~ end
# ~\~ end
