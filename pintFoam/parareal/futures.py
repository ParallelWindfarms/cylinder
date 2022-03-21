# ~\~ language=Python filename=pintFoam/parareal/futures.py
# ~\~ begin <<lit/parafutures.md|pintFoam/parareal/futures.py>>[0]
from .abstract import (Solution, Mapping)
from typing import Any
import numpy as np
from numpy.typing import NDArray
from dask.distributed import Client, Future

def identity(x):
    return x

def parareal(
        coarse: Solution,
        fine: Solution,
        c2f: Mapping = identity,
        f2c: Mapping = identity):
    """Implementation of Parareal, based on Dask futures. The `coarse` and `fine`
    arguments should be normal functions (i.e. not delayed)."""
    def f(y, t):
        m = t.size
        y_n = [None] * m
        y_n[0] = y[0]
        for i in range(1, m):
            y_n[i] = c2f(coarse(f2c(y_n[i-1]), t[i-1], t[i])) \
                   + fine(y[i-1], t[i-1], t[i]) \
                   - c2f(coarse(f2c(y[i-1]), t[i-1], t[i]))
        return y_n
    return f
# ~\~ end
