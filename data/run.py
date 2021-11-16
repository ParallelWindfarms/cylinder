# ~\~ language=Python filename=data/run.py
# ~\~ begin <<lit/cylinder.md|data/run.py>>[0]
from pathlib import Path
import numpy as np
from noodles import (gather)
from functools import partial
from paranoodles import (schedule, run, parareal, tabulate)
from pintFoam import (BaseCase, foam, block_mesh, serial)


case = BaseCase(Path("c1"), "baseCase", fields=["p", "U", "phi", "phi_0", "pMean", "pPrime2Mean", "U_0", "UMean", "UPrime2Mean"])
block_mesh(case)

times = np.linspace(0.0, 350.0, 11)

@schedule
def fine(n, x, t_0, t_1):
    """Fine integrator."""
    return foam("icoFoam", 0.05, x, t_0, t_1,
                job_name=f"{n}-{int(t_0):03}-{int(t_1):03}-fine")


@schedule
def coarse(n, x, t_0, t_1):
    """Coarse integrator."""
    return foam("icoFoam", 1.0, x, t_0, t_1,
                job_name=f"{n}-{int(t_0):03}-{int(t_1):03}-coarse")

# init = foam("icoFoam", 0.0001, case.new_vector(), 0.0, 0.0)
init = case.new_vector("init")
y = gather(*tabulate(partial(coarse, 0), init, times))

for n in range(1, 10):
    y = gather(*parareal(partial(coarse, n), partial(fine, n))(y, times))

run(y, n_threads=4, registry=serial, db_file="noodles.db")
# ~\~ end
