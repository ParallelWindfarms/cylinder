# ~\~ language=Python filename=pintFoam/parareal/parareal.py
# ~\~ begin <<lit/paranoodles.md|pintFoam/parareal/parareal.py>>[0]
from .abstract import (Solution, Mapping)

def identity(x):
    return x

# ~\~ end
# ~\~ begin <<lit/paranoodles.md|pintFoam/parareal/parareal.py>>[1]
def parareal(
        coarse: Solution,
        fine: Solution,
        c2f: Mapping = identity,
        f2c: Mapping = identity):
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
# ~\~ end
