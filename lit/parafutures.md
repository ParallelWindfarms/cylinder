# Implementation of Parareal using Futures
We reimplement Parareal in the `futures` framework of Dask::

``` {.python #parareal-step}
@dataclass
class Parareal:
    client: Client
    coarse: Solution
    fine: Solution
    c2f: Mapping
    f2c: Mapping

    def _c2f(self, x):
        return self.client.submit(self.c2f, x)

    def _f2c(self, x):
        return self.client.submit(self.f2c, x)

    def _coarse(self, y, t0, t1):
        return self.client.submit(self.coarse, y, t0, t1)

    def _fine(self, y, t0, t1):
        return self.client.submit(self.fine, y, t0, t1)

    def step(self, y_prev: list[Future], t: NDArray[np.float64]):
        m = t.size
        y_next = [None] * m
        y_next[0] = y_prev[0]

        for i in range(1, m):
            f_ self._c2f(self._course(self.f2c(y_next[i-1]), t[i-1], t[i]))
```

``` {.python file=pintFoam/parareal/futures.py}
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
```
