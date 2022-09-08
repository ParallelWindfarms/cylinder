# Example using MPI and Dask Futures

``` {.python file=examples/mpi_futures.py #example-mpi}
from __future__ import annotations
import argh  # type: ignore
import numpy as np
# import numpy.typing as npt
from pathlib import Path
from dataclasses import dataclass, field
from typing import (Union, Callable, Optional, Any, Iterator)
from abc import (ABC, abstractmethod)
<<example-mpi-imports>>

OMEGA0 = 1.0
ZETA = 0.1
H = 0.001

<<vector-expressions>>
<<example-mpi-coarse>>
<<example-mpi-fine>>
<<example-mpi-history>>

def get_data(files: list[Path]) -> Iterator[np.ndarray]:
    for n in files:
        with h5.File(n, "r") as f:
            yield f["data"][:]

def combine_fine_data(files: list[Path]) -> np.ndarray:
    data = get_data(files)
    first = next(data)
    return np.concatenate([first] + [x[1:] for x in data], axis=0)

# def list_files(path: Path) -> list[Path]:
#     all_files = path.glob("*.h5")
#     return []

def main(log: str = "WARNING", log_file: Optional[str] = None):
    """Run model of dampened hormonic oscillator in Dask"""
    log_level = getattr(logging, log.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level `{log}`")
    logging.basicConfig(level=log_level, filename=log_file)
    <<example-mpi-main>>

if __name__ == "__main__":
    import time
    argh.dispatch_command(main)
    time.sleep(10)
```

There are two modes in which we may run Dask with MPI. One with a `dask-mpi` running as external scheduler, the other running everything as a single script. For this example we opt for the second, straight from the dask-mpi documentation:

``` {.python #example-mpi-imports}
from dask_mpi import initialize  # type: ignore
from dask.distributed import Client  # type: ignore
# from mpi4py import MPI
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
    def reduce(self: Vector) -> np.ndarray:
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
def reduce_expr(expr: Union[np.ndarray, Vector]) -> np.ndarray:
    if isinstance(expr, Vector):
        return expr.reduce()
    else:
        return expr
```

### HDF5 Vectors
This means we can also hide variables that are stored in an HDF5 file behind this interface:

``` {.python #vector-expressions}
@dataclass
class H5Snap(Vector):
    path: Path
    loc: str
    slice: list[Union[None, int, slice]]

    def data(self):
        with h5.File(self.path, "r") as f:
            return f[self.loc].__getitem__(tuple(self.slice))

    def reduce(self):
        x = self.data()
        logger = logging.getLogger()
        logger.debug(f"read {x} from {self.path}")
        return self.data()
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

    def reduce(self):
        a = reduce_expr(self.inp)
        return self.func(a)


@dataclass
class BinaryExpr(Vector):
    func: Callable[[np.ndarray, np.ndarray], np.ndarray]
    inp1: Vector
    inp2: Vector

    def reduce(self):
        a = reduce_expr(self.inp1)
        b = reduce_expr(self.inp2)
        return self.func(a, b)
```

### Literal expressions
To bootstrap our computation we may need to define a `Vector` directly represented by a Numpy array.

``` {.python #vector-expressions}
@dataclass
class LiteralExpr(Vector):
    value: np.ndarray

    def reduce(self):
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
```

``` {.python #example-mpi-main}
OMEGA0 = 1.0
ZETA = 1.0
H = 0.001
system = harmonic_oscillator(OMEGA0, ZETA)
```

``` {.python #example-mpi-coarse}
@dataclass
class Coarse:
    n_iter: int
    system: Any
    system = harmonic_oscillator(OMEGA0, ZETA)

    def solution(self, y, t0, t1):
        a = LiteralExpr(forward_euler(self.system)(reduce_expr(y), t0, t1))
        logging.debug(f"coarse result: {y} {reduce_expr(y)} {t0} {t1} {a}")
        return a
```

``` {.python #example-mpi-fine}
def generate_filename(name: str, n_iter: int, t0: float, t1: float) -> str:
    return f"{name}-{n_iter:04}-{int(t0*1000):06}-{int(t1*1000):06}.h5"

@dataclass
class Fine:
    parent: Path
    name: str
    n_iter: int
    system: Any
    h: float

    def solution(self, y, t0, t1):
        logger = logging.getLogger()
        n = math.ceil((t1 - t0) / self.h)
        t = np.linspace(t0, t1, n + 1)

        self.parent.mkdir(parents=True, exist_ok=True)
        path = self.parent / generate_filename(self.name, self.n_iter, t0, t1)

        with h5.File(path, "w") as f:
            logger.debug("fine %f - %f", t0, t1)
            y0 = reduce_expr(y)
            logger.debug(":    %s -> %s", y, y0)
            x = tabulate(forward_euler(self.system), reduce_expr(y), t)
            ds = f.create_dataset("data", data=x)
            ds.attrs["t0"] = t0
            ds.attrs["t1"] = t1
            ds.attrs["h"] = self.h
            ds.attrs["n"] = n
        return H5Snap(path, "data", index[-1])
```

``` {.python #example-mpi-main}
y0 = np.array([1.0, 0.0])
t = np.linspace(0.0, 15.0, 20)
archive = Path("./output/euler")
underdamped_solution(OMEGA0, ZETA)(t)
tabulate(Fine(archive, "fine", 0, system, H).solution, LiteralExpr(y0), t)

# euler_files = archive.glob("*.h5")
```


``` {.python #example-mpi-history}
@dataclass
class History:
    archive: Path
    history: list[list[Vector]] = field(default_factory=list)

    def convergence_test(self, y) -> bool:
        logger = logging.getLogger()
        self.history.append(y)
        if len(self.history) < 2:
            return False
        a = np.array([reduce_expr(x) for x in self.history[-2]])
        b = np.array([reduce_expr(x) for x in self.history[-1]])
        maxdif = np.abs(a - b).max()
        converged = maxdif < 1e-4
        logger.info("maxdif of %f", maxdif)
        if converged:
            logger.info("Converged after %u iteration", len(self.history))
        return converged
```

``` {.python #example-mpi-main}
archive = Path("./output/parareal")
p = Parareal(
    client,
    lambda n: Coarse(n, system).solution,
    lambda n: Fine(archive, "fine", n, system, H).solution)
jobs = p.schedule(LiteralExpr(y0), t)
history = History(archive)
p.wait(jobs, history.convergence_test)
```

