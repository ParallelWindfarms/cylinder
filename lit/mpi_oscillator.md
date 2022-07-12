# Example using MPI and Dask Futures

``` {.python file=examples/mpi_futures.py #example-mpi}
from __future__ import annotations
import numpy as np
# import numpy.typing as npt
from pathlib import Path
from dataclasses import dataclass, field
from typing import (Union, Callable)
from abc import (ABC, abstractmethod)
<<example-mpi-imports>>

<<vector-expressions>>
<<example-mpi-coarse>>
<<example-mpi-fine>>
<<example-mpi-history>>

if __name__ == "__main__":
    <<example-mpi-main>>
```

There are two modes in which we may run Dask with MPI. One with a `dask-mpi` running as external scheduler, the other running everything as a single script. For this example we opt for the second, straight from the dask-mpi documentation:

``` {.python #example-mpi-imports}
from dask_mpi import initialize  # type: ignore
from dask.distributed import Client  # type: ignore
from mpi4py import MPI
```

``` {.python #example-mpi-main}
initialize()
client = Client()
```

## Vector Arithmetic Expressions
The following technique is definitely overkill for our harmonic oscillator example, but it is also in general a good recipe for running Numpy based simulations in an organized manner.

It may be convenient to treat our `Vector` operations such that they are only performed once their output is needed. In the meantime we have to store the arithmetic in a serializable `Expression` value.

We will be using `functools.partial` and functions `operator.add`, `operator.mul` etc, to create a data structure that describes all the operations that we might do on a `Vector`. Results may be stored for reference in a `hdf5` file, a feature that can also be hidden behind our `Vector` interface.

``` {.python #example-mpi-imports}
import operator
from functools import partial
import h5py as h5  # type: ignore
```

We create a `Vector` class that satisfies the `Vector` concept outlined earlier. We store the operations in terms of unary and binary operators.

``` {.python #vector-expressions}
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
```

The `Vector` class acts as a base class for the implementation of `BinaryExpr` and `UnaryExpr`, so that we can nest expressions accordingly. To force computation of a `Vector`, we supply the `reduce_expr` function that, in an example of terrible duck-typing, calls the `reduce` method recursively, until an object is reached that doesn't have the `reduce` method.

``` {.python #vector-expressions}
def reduce_expr(expr: Union[np.ndarray, Vector], f: h5.File) -> np.ndarray:
    if not isinstance(expr, np.ndarray):
        return expr.reduce(f)
    else:
        return expr
```

### HDF5 Vectors
This means we can also hide variables that are stored in an HDF5 file behind this interface:

``` {.python #vector-expressions}
@dataclass
class H5Snap(Vector):
    loc: str
    slice: list[Union[None, int, slice]]

    def data(self, f):
        return f[self.loc].__getitem__(tuple(self.slice))

    def reduce(self, f):
        return self.data(f)
```

To generate slices in a nice manner we can use a helper class:

``` {.python #vector-expressions}
class Index:
    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            return list(idx)
        else:
            return [idx]

index = Index()
```

### Operators
There are two classes of operators, unary and binary (more arguments can usually be expressed as a composition of unary and binary forms). We store the arguments together with a function operating on the arguments. The function should be serializable (e.g. using `pickle`), meaning that `lambda` expressions are not allowed, but `partial` applications and functions in `operator` typically are ok.

``` {.python #vector-expressions}
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
```

### Literal expressions
To bootstrap our computation we may need to define a `Vector` directly represented by a Numpy array.

``` {.python #vector-expressions}
@dataclass
class LiteralExpr(Vector):
    value: np.ndarray

    def reduce(self, f):
        return self.value
```

## Running the harmonic oscillator

``` {.python #example-mpi-imports}
from pintFoam.parareal.futures import (Parareal)

from pintFoam.parareal.forward_euler import forward_euler
# from pintFoam.parareal.iterate_solution import iterate_solution
from pintFoam.parareal.tabulate_solution import tabulate
from pintFoam.parareal.harmonic_oscillator import (underdamped_solution, harmonic_oscillator)

import math
# from uuid import uuid4
import logging

logging.basicConfig()
```

``` {.python #example-mpi-main}
OMEGA0 = 1.0
ZETA = 0.5
H = 0.001
system = harmonic_oscillator(OMEGA0, ZETA)
```

``` {.python #example-mpi-coarse}
@dataclass
class Coarse:
    archive: Path
    n_iter: int

    def solution(self, y, t0, t1):
        with h5.File(self.archive, "a") as f:
            return LiteralExpr(forward_euler(system)(reduce_expr(y, f), t0, t1))
```

``` {.python #example-mpi-fine}
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
```

``` {.python #example-mpi-main}
y0 = np.array([1.0, 0.0])
t = np.linspace(0.0, 15.0, 10)
archive = Path("./harmonic-oscillator-euler.h5")
exact_result = underdamped_solution(OMEGA0, ZETA)(t)
euler_result = tabulate(Fine(archive, 0).solution, LiteralExpr(y0), t)
```


``` {.python #example-mpi-history}
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
```

``` {.python #example-mpi-main}
archive = Path("./harmonic-oscillator-parareal.h5")
p = Parareal(
    client,
    lambda n: Coarse(archive, n).solution,
    lambda n: Fine(archive, n).solution)
jobs = p.schedule(LiteralExpr(y0), t)
history = History(archive)
p.wait(jobs, history.convergence_test)
```

