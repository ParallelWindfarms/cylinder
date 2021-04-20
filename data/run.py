# ~\~ language=Python filename=data/run.py
# ~\~ begin <<lit/cylinder.md|data/run.py>>[0]
from pathlib import Path
import numpy as np
from paranoodles import (schedule, run, parareal, tabulate)
from pintFoam import (BaseCase, foam, block_mesh, serial)


case = BaseCase(Path("c1"), "baseCase")
block_mesh(case)


@schedule
def fine(x, t_0, t_1):
    return foam("icoFoam", 0.05, x, t_0, t_1)


@schedule
def coarse(x, t_0, t_1):
    return foam("icoFoam", 0.2, x, t_0, t_1)


times = np.linspace(0.0, 10.0, 100)
init = foam("icoFoam", 0.05, case.new_vector(), 0.0, 0.0)
tabulate(parareal(coarse, fine), init, times)
# ~\~ end
