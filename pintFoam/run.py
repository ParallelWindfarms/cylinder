# ~\~ language=Python filename=pintFoam/run.py
# ~\~ begin <<lit/cylinder.md|pintFoam/run.py>>[0]
from .solution import foam
from dask import delayed

@delayed
def fine(x, t_0, t_1):
    """Example fine integrator."""
    return foam("icoFoam", 0.05, x, t_0, t_1)

@delayed
def coarse(x, t_0, t_1):
    """Example coarse integrator."""
    return foam("icoFoam", 0.2, x, t_0, t_1)

# ~\~ end
