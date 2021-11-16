from pathlib import Path
from collections.abc import Sequence
import numpy as np
from math import ceil

from dask import delayed
from functools import partial
from paranoodles import (parareal, tabulate)
from pintFoam import (BaseCase, foam, block_mesh, serial)
from pintFoam.vector import (Vector)
from pintFoam.solution import (map_fields)

fields = ["p", "U", "phi", "phi_0", "pMean", "pPrime2Mean", "U_0", "UMean", "UPrime2Mean"]

fine_case = BaseCase(Path("c7_fine"), "baseCase", fields=fields)
coarse_case = BaseCase(Path("c7_coarse"), "baseCase", fields=fields)
block_mesh(fine_case)
block_mesh(coarse_case)

times = np.linspace(0, 50, 51)

@delayed
def gather(*args):
    return list(args)


@delayed
def c2f(x):
    """Coarse to fine.
    
    Interpolate the underlying field x from the coarse to the fine grid"""
    return map_fields(x, fine_case, map_method="interpolate")


@delayed
def f2c(x):
    """Fine to coarse.
    
    Interpolate the underlying field x from the fine to the coarse grid"""
    return map_fields(x, coarse_case, map_method="interpolate")


@delayed
def fine(n, x, t_0, t_1):
    """Fine integrator."""
    return foam("pimpleFoam", 0.1, x, t_0, t_1,
                job_name=f"{n}-{int(t_0):03}-{int(t_1):03}-fine")


@delayed
def coarse(n, x, t_0, t_1):
    """Coarse integrator."""
    return foam("pimpleFoam", 1.0, x, t_0, t_1,
                job_name=f"{n}-{int(t_0):03}-{int(t_1):03}-coarse")


def time_windows(times, window_size):
    """Split the times vector in a set of time windows of a given size.
    
    Args:
        times:          The times vector
        window_size:    The number of steps per window (note that n steps 
        correspond to n + 1 elements in the window). The last window may 
        be smaller.
    """
    n_intervals = len(times) - 1
    n = int(ceil(n_intervals / window_size))
    m = window_size
    return [times[i*m:min(i*m+m+1, len(times))] for i in range(n)]


def solve(init: Vector, times: Sequence[float], max_iter=1) -> list[Vector]:
    # coarse initial integration from fine initial condition
    y = gather(*map(c2f, tabulate(partial(coarse, 0), f2c(init), times)))
    for n in range(1, max_iter+1):
        y = gather(*parareal(partial(coarse, n), partial(fine, n), c2f, f2c)(y, times))
    return y.compute()


def windowed(times, init, window_size):
    windows = time_windows(times, window_size)
    result = [init]
    for w in windows:
        w_result = solve(result[-1], w)
        result.extend(w_result)
    return result


print(time_windows(np.arange(40), 11))
init = fine_case.new_vector()
wf = solve(init, np.arange(3))

