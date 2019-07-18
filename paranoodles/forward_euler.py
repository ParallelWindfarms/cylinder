## ------ language="Python" file="paranoodles/forward_euler.py"
from .abstract import (Vector, Problem, Solution)

def forward_euler(f: Problem) -> Solution:
    def step(y: Vector, t_0: float, t_1: float) -> Vector:
        """Stepping function of Euler method."""
        return y + (t_1 - t_0) * f(y, t_0)
    return step
## ------ end
