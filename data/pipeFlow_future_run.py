from pathlib import Path
from collections.abc import Sequence
import numpy as np
from numpy.typing import NDArray
import logging
import uuid

from dataclasses import dataclass, field
from dask.distributed import Client  # type: ignore
from functools import partial
from pintFoam.parareal import (parareal, tabulate)
from pintFoam import (BaseCase, foam, block_mesh)
from pintFoam.vector import (Vector)
from pintFoam.parareal.futures import (Parareal)
from pintFoam.foam import (map_fields)
from pintFoam.utils import (generate_job_name)

## Problem specification
fields = ["p", "U"]
case_name = "pipeFlow"

fine_case = BaseCase(Path(case_name + "Fine"), "baseCase", fields=fields)
coarse_case = BaseCase(Path(case_name + "Coarse"), "baseCase", fields=fields)

fine_case.clean()
coarse_case.clean()

block_mesh(fine_case)
block_mesh(coarse_case)

times = np.linspace(0, 2, 21)

def fine(n, x, t_0, t_1):
    """Fine integrator."""
    uid = uuid.uuid4()
    return foam("pimpleFoam", 0.001, x, t_0, t_1,
                job_name=generate_job_name(n, t_0, t_1, uid, "fine"))


def coarse(n, x, t_0, t_1):
    """Coarse integrator."""
    uid = uuid.uuid4()
    return foam("pimpleFoam", 0.1, x, t_0, t_1,
                job_name=generate_job_name(n, t_0, t_1, uid, "coarse"))

def c2f(x):
    """Coarse to fine.

    Interpolate the underlying field x from the coarse to the fine grid"""
    return map_fields(x, fine_case, map_method="interpolate")


def f2c(x):
    """Fine to coarse.

    Interpolate the underlying field x from the fine to the coarse grid"""
    return map_fields(x, coarse_case, map_method="interpolate")


@dataclass
class History:
    history: list[NDArray[np.float64]] = field(default_factory=list)

    def convergence_test(self, y):
        self.history.append(np.array(y))
        logging.debug("got result: %s", self.history[-1])
        if len(self.history) < 2:
            return False
        return np.allclose(self.history[-1], self.history[-2], atol=1e-4)


client = Client()
p = Parareal(client, 
             lambda n: partial(coarse, n), 
             lambda n: partial(fine, n), 
             c2f,
             f2c)
t = np.linspace(0.0, 15.0, 30)
y0 = fine_case.new_vector()
history = History()
jobs = p.schedule(y0, t)
p.wait(jobs, history.convergence_test)
