## ------ language="Python" file="paranoodles/iterate_solution.py"
from .abstract import (Vector, Problem, Solution)
import numpy as np

def iterate_solution(step: Solution, h: float) -> Solution:
    def iter_step(y: Vector, t_0: float, t_1: float) -> Vector:
        """Stepping function of iterated solution."""
        n = math.ceil((t_1 - t_0) / h)
        steps = np.arange(t_0, t_1, n + 1)
        for t_a, t_b in zip(steps[:-1], steps[1:])
            y = step(y, t_a, t_b)
        return y         
    return iter_step
## ------ end
