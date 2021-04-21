# ~\~ language=Python filename=data/run.py
# ~\~ begin <<lit/cylinder.md|data/run.py>>[0]
from pathlib import Path
import numpy as np
from noodles import (gather)
from paranoodles import (schedule, run, parareal, tabulate)
from pintFoam import (BaseCase, foam, block_mesh, serial)


case = BaseCase(Path("c1"), "baseCase")
block_mesh(case)


@schedule
def fine(x, t_0, t_1):
    return foam("icoFoam", 0.05, x, t_0, t_1)


@schedule
def coarse(x, t_0, t_1):
    return foam("icoFoam", 1.0, x, t_0, t_1)


times = np.linspace(0.0, 350.0, 11)
# init = foam("icoFoam", 0.0001, case.new_vector(), 0.0, 0.0)
init = case.new_vector("init")
y_first = gather(*tabulate(coarse, init, times))
y_parareal = gather(*parareal(coarse, fine)(y_first, times))

run(y_parareal, n_threads=4, registry=serial, db_file="noodles.db")
# ~\~ end
