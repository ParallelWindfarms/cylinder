# ~\~ language=Python filename=pintFoam/run.py
# ~\~ begin <<lit/cylinder.md|pintFoam/run.py>>[0]
import noodles   # type: ignore
from noodles import serial

from .solution import foam

@noodles.schedule
def fine(x, t_0, t_1):
    return foam("icoFoam", 0.05, x, t_0, t_1)

@noodles.schedule
def coarse(x, t_0, t_1):
    return foam("icoFoam", 0.2, x, t_0, t_1)

def registry():
    return serial.base() + serial.numpy()
# ~\~ end
