# ~\~ language=Python filename=paranoodles/parareal.py
# ~\~ begin <<lit/paranoodles.md|paranoodles/parareal.py>>[0]
from .abstract import (Solution)

def parareal(coarse: Solution, fine: Solution):
    def f(y, t):
        m = t.size
        y_n = [None] * m
        y_n[0] = y[0]
        for i in range(1, m):
            # ~\~ begin <<lit/paranoodles.md|parareal-core>>[0]
            y_n[i] = coarse(y_n[i-1], t[i-1], t[i]) \
                   + fine(y[i-1], t[i-1], t[i]) \
                   - coarse(y[i-1], t[i-1], t[i])
            # ~\~ end
        return y_n

    return f
# ~\~ end
