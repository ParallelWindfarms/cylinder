# ~\~ language=Python filename=test/test_futures.py
# ~\~ begin <<lit/parafutures.md|test/test_futures.py>>[0]
from dataclasses import dataclass, field
import logging
from numpy.typing import NDArray
import numpy as np

from pintFoam.parareal.futures import Parareal
from pintFoam.parareal.harmonic_oscillator import harmonic_oscillator
from pintFoam.parareal.forward_euler import forward_euler
from pintFoam.parareal.iterate_solution import iterate_solution
from pintFoam.parareal.tabulate_solution import tabulate

from dask.distributed import Client  # type: ignore


OMEGA0 = 1.0
ZETA = 0.5
H = 0.001
system = harmonic_oscillator(OMEGA0, ZETA)


def coarse(y, t0, t1):
    return forward_euler(system)(y, t0, t1)


def fine(y, t0, t1):
    return iterate_solution(forward_euler(system), H)(y, t0, t1)


@dataclass
class History:
    history: list[NDArray[np.float64]] = field(default_factory=list)

    def convergence_test(self, y):
        self.history.append(np.array(y))
        logging.debug("got result: %s", self.history[-1])
        if len(self.history) < 2:
            return False
        return np.allclose(self.history[-1], self.history[-2], atol=1e-4)


def test_parareal():
    client = Client()
    p = Parareal(client, coarse, fine)
    t = np.linspace(0.0, 15.0, 30)
    y0 = np.array([0.0, 1.0])
    history = History()
    jobs = p.schedule(y0, t)
    p.wait(jobs, history.convergence_test)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    y0 = np.array([1.0, 0.0])
    t = np.linspace(0.0, 15.0, 30)
    result = tabulate(fine, y0, t)
    print(result)
# ~\~ end
