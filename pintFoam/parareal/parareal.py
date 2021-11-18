# ~\~ language=Python filename=pintFoam/parareal/parareal.py
# ~\~ begin <<lit/paranoodles.md|pintFoam/parareal/parareal.py>>[0]
from .abstract import (Solution, Mapping)

def identity(x):
    return x

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
            # ~\~ begin <<lit/paranoodles.md|parareal-core-2>>[0]
            y_n[i] = c2f(coarse(f2c(y_n[i-1]), t[i-1], t[i])) \
                   + fine(y[i-1], t[i-1], t[i]) \
                   - c2f(coarse(f2c(y[i-1]), t[i-1], t[i]))
            # ~\~ end
            # ~\~ begin <<lit/parareal.md|parareal-core-2>>[0]
            y_n[i] = c2f(coarse(f2c(y_n[i-1]), t[i-1], t[i])) \
                   + fine(y[i-1], t[i-1], t[i]) \
                   - c2f(coarse(f2c(y[i-1]), t[i-1], t[i]))
            # ~\~ end
        return y_n
    return f
# ~\~ end
# ~\~ begin <<lit/parareal.md|pintFoam/parareal/parareal.py>>[0]
from .abstract import (Solution, Mapping)

def identity(x):
    return x

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
            # ~\~ begin <<lit/paranoodles.md|parareal-core-2>>[0]
            y_n[i] = c2f(coarse(f2c(y_n[i-1]), t[i-1], t[i])) \
                   + fine(y[i-1], t[i-1], t[i]) \
                   - c2f(coarse(f2c(y[i-1]), t[i-1], t[i]))
            # ~\~ end
            # ~\~ begin <<lit/parareal.md|parareal-core-2>>[0]
            y_n[i] = c2f(coarse(f2c(y_n[i-1]), t[i-1], t[i])) \
                   + fine(y[i-1], t[i-1], t[i]) \
                   - c2f(coarse(f2c(y[i-1]), t[i-1], t[i]))
            # ~\~ end
        return y_n
    return f
# ~\~ end
