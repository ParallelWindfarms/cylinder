## ------ language="Python" file="paranoodles/harmonic_oscillator.py"
from .abstract import (Problem)
import numpy as np

def harmonic_oscillator(omega_0: float, zeta: float) -> Problem:
    def f(y, t):
        return np.r_[y[1], -2 * zeta * omega_0 * y[1] - omega_0**2 * y[0]]
    return f
    
## ------ begin <<harmonic-oscillator-solution>>[0]
def underdamped_solution(omega_0: float, zeta: float) -> np.ndarray:
    amp   = 1 / np.sqrt(1 - zeta**2)
    phase = np.arcsin(zeta)
    freq  = omega_0 * np.sqrt(1 - zeta**2)

    def f(t):
        dampening = np.exp(-omega_0*zeta*t)
        q = amp * dampening * np.cos(freq * t - phase)
        p = - amp * omega_0 * dampening * np.sin(freq * t)
        return np.c_[q, p]
    return f
## ------ end
## ------ end
