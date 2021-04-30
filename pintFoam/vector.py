# ~\~ language=Python filename=pintFoam/vector.py
# ~\~ begin <<lit/cylinder.md|pintFoam/vector.py>>[0]
from __future__ import annotations

import operator
import mmap

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from shutil import copytree, rmtree   # , copy
from typing import List, Optional

from byteparsing import parse_bytes, foam_file
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
    fields: Optional[List[str]] = None

    @property
    def path(self):
        return self.root / self.case

    def new_vector(self, name: Optional[str] = None):
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


def get_times(path):
    """Get all the snapshots in a case, sorted on floating point value."""
    def isfloat(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    return sorted(
        [s.name for s in path.iterdir() if isfloat(s.name)],
        key=float)
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
        """Case path, i.e. the path containing `system`, `constant` and snapshots."""
        return self.base.root / self.case

    @property
    def fields(self):
        """All fields relevant to this base case."""
        return self.base.fields

    @property
    def dirname(self):
        """The path of this snapshot."""
        return self.path / self.time

    def all_times(self):
        """Get all available times, in order."""
        return [Vector(self.base, self.case, t)
                for t in get_times(self.path)]

    @contextmanager
    def mmap_data(self, field):
        """Context manager that yields a **mutable** reference to the data contained
        in this snapshot. Mutations done to this array are mmapped to the disk directly."""
        f = (self.dirname / field).open(mode="r+b")
        with mmap.mmap(f.fileno(), 0) as mm:
            content = parse_bytes(foam_file, mm)
            try:
                yield content["data"]["internalField"]
            except KeyError as e:
                print(content)
                raise e
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-clone>>[0]
    def clone(self, name: Optional[str] = None) -> Vector:
        """Clone this vector to a new one. The clone only contains this single snapshot."""
        x = self.base.new_vector(name)
        x.time = self.time
        rmtree(x.dirname, ignore_errors=True)
        copytree(self.dirname, x.dirname)
        return x
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-operate>>[0]
    def zip_with(self, other: Vector, op) -> Vector:
        x = self.clone()
        # ~\~ begin <<lit/cylinder.md|copy-attrs-and-bounds>>[0]
        # We're back to mutating a clone, so no copying of attrs needed.
        # ~\~ end

        for f in self.fields:
            with x.mmap_data(f) as a, other.mmap_data(f) as b:
                a[:] = op(a, b)
        return x

    def map(self, f) -> Vector:
        x = self.clone()

        for f in self.fields:
            with x.mmap_data(f) as a:
                a[:] = f(a)
        return x
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|pintfoam-vector-operators>>[0]
    def __sub__(self, other: Vector) -> Vector:
        return self.zip_with(other, operator.sub)

    def __add__(self, other: Vector) -> Vector:
        return self.zip_with(other, operator.add)

    def __mul__(self, scale: float) -> Vector:
        return self.map(lambda x: x * scale)
    # ~\~ end
# ~\~ end
# ~\~ end
