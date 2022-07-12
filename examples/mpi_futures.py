# ~\~ language=Python filename=examples/mpi_futures.py
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi>>[init]
from __future__ import annotations
import numpy as np
# import numpy.typing as npt
from pathlib import Path
from dataclasses import dataclass, field
from typing import (Union, Callable)
from abc import (ABC, abstractmethod)
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi-imports>>[init]
from dask_mpi import initialize  # type: ignore
from dask.distributed import Client  # type: ignore
from mpi4py import MPI
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi-imports>>[1]
import operator
from functools import partial
import h5py as h5  # type: ignore
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi-imports>>[2]
from pintFoam.parareal.futures import (Parareal)

from pintFoam.parareal.forward_euler import forward_euler
# from pintFoam.parareal.iterate_solution import iterate_solution
from pintFoam.parareal.tabulate_solution import tabulate
from pintFoam.parareal.harmonic_oscillator import (underdamped_solution, harmonic_oscillator)

import math
# from uuid import uuid4
import logging

logging.basicConfig()
# ~\~ end

# ~\~ begin <<lit/mpi_oscillator.md|vector-expressions>>[init]
class Vector(ABC):
    @abstractmethod
    def reduce(self: Vector, f: h5.File) -> np.ndarray:
        pass

    def __add__(self, other):
        return BinaryExpr(operator.add, self, other)

    def __sub__(self, other):
        return BinaryExpr(operator.sub, self, other)

    def __mul__(self, scale):
        return UnaryExpr(partial(operator.mul, scale), self)

    def __rmul__(self, scale):
        return UnaryExpr(partial(operator.mul, scale), self)
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|vector-expressions>>[1]
def reduce_expr(expr: Union[np.ndarray, Vector], f: h5.File) -> np.ndarray:
    if not isinstance(expr, np.ndarray):
        return expr.reduce(f)
    else:
        return expr
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|vector-expressions>>[2]
@dataclass
class H5Snap(Vector):
    loc: str
    slice: list[Union[None, int, slice]]

    def data(self, f):
        return f[self.loc].__getitem__(tuple(self.slice))

    def reduce(self, f):
        return self.data(f)
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|vector-expressions>>[3]
class Index:
    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            return list(idx)
        else:
            return [idx]

index = Index()
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|vector-expressions>>[4]
@dataclass
class UnaryExpr(Vector):
    func: Callable[[np.ndarray], np.ndarray]
    inp: Vector

    def reduce(self, f):
        a = reduce_expr(self.inp, f)
        return self.func(a)


@dataclass
class BinaryExpr(Vector):
    func: Callable[[np.ndarray, np.ndarray], np.ndarray]
    inp1: Vector
    inp2: Vector

    def reduce(self, f):
        a = reduce_expr(self.inp2, f)
        b = reduce_expr(self.inp2, f)
        return self.func(a, b)
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|vector-expressions>>[5]
@dataclass
class LiteralExpr(Vector):
    value: np.ndarray

    def reduce(self, f):
        return self.value
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi-coarse>>[init]
@dataclass
class Coarse:
    archive: Path
    n_iter: int

    def solution(self, y, t0, t1):
        with h5.File(self.archive, "a") as f:
            return LiteralExpr(forward_euler(system)(reduce_expr(y, f), t0, t1))
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi-fine>>[init]
@dataclass
class Fine:
    archive: Path
    n_iter: int

    def solution(self, y, t0, t1):
        logger = logging.getLogger()
        n = math.ceil((t1 - t0) / H)
        t = np.linspace(t0, t1, n + 1)
        with h5.File(self.archive, "a", driver='mpio', comm=MPI.COMM_WORLD) as f:
            logger.debug("fine %f - %f", t0, t1)
            y0 = reduce_expr(y, f)
            logger.debug("    %s", y0)
            x = tabulate(forward_euler(system), reduce_expr(y, f), t)

            loc = f"{self.n_iter:04}/fine-{int(t0*1000):06}-{int(t1*1000):06}"
            ds = f.create_dataset(loc, data=x)
            ds.attrs["t0"] = t0
            ds.attrs["t1"] = t1
            ds.attrs["n"] = n
        return H5Snap(loc, index[-1])
# ~\~ end
# ~\~ begin <<lit/mpi_oscillator.md|example-mpi-history>>[init]
@dataclass
class History:
    archive: Path
    history: list[Vector] = field(default_factory=list)

    def convergence_test(self, y) -> bool:
        self.history.append(y)
        if len(self.history) < 2:
            return False
        with h5.File(self.archive, "r") as f:
            a = reduce_expr(self.history[-2], f)
            b = reduce_expr(self.history[-1], f)
            return np.allclose(a, b, atol=1e-4)
# ~\~ end

if __name__ == "__main__":
    # ~\~ begin <<lit/mpi_oscillator.md|example-mpi-main>>[init]
    initialize()
    client = Client()
    # ~\~ end
    # ~\~ begin <<lit/mpi_oscillator.md|example-mpi-main>>[1]
    OMEGA0 = 1.0
    ZETA = 0.5
    H = 0.001
    system = harmonic_oscillator(OMEGA0, ZETA)
    # ~\~ end
    # ~\~ begin <<lit/mpi_oscillator.md|example-mpi-main>>[2]
    y0 = np.array([1.0, 0.0])
    t = np.linspace(0.0, 15.0, 10)
    archive = Path("./harmonic-oscillator-euler.h5")
    exact_result = underdamped_solution(OMEGA0, ZETA)(t)
    euler_result = tabulate(Fine(archive, 0).solution, LiteralExpr(y0), t)
    # ~\~ end
    # ~\~ begin <<lit/mpi_oscillator.md|example-mpi-main>>[3]
    archive = Path("./harmonic-oscillator-parareal.h5")
    p = Parareal(
        client,
        lambda n: Coarse(archive, n).solution,
        lambda n: Fine(archive, n).solution)
    jobs = p.schedule(LiteralExpr(y0), t)
    history = History(archive)
    p.wait(jobs, history.convergence_test)
    # ~\~ end
# ~\~ end
