# ~\~ language=Python filename=examples/harmonic_oscillator.py
# ~\~ begin <<lit/paranoodles.md|examples/harmonic_oscillator.py>>[0]
# ~\~ begin <<lit/paranoodles.md|plot-harmonic-oscillator>>[0]
import matplotlib.pylab as plt
import numpy as np

from pintFoam.parareal.harmonic_oscillator import \
    ( harmonic_oscillator, underdamped_solution )
from pintFoam.parareal.forward_euler import \
    ( forward_euler )
from pintFoam.parareal.tabulate_solution import \
    ( tabulate )

omega_0 = 1.0
zeta = 0.5
f = harmonic_oscillator(omega_0, zeta)
t = np.linspace(0.0, 15.0, 100)
y_euler = tabulate(forward_euler(f), np.r_[1.0, 0.0], t)
y_exact = underdamped_solution(omega_0, zeta)(t)

plt.plot(t, y_euler[:,0], color='slateblue', label="euler")
plt.plot(t, y_exact[:,0], color='k', label="exact")
plt.plot(t, y_euler[:,1], color='slateblue', linestyle=':')
plt.plot(t, y_exact[:,1], color='k', linestyle=':')
plt.legend()
plt.savefig("harmonic.svg")
# ~\~ end

# ~\~ begin <<lit/paranoodles.md|daskify>>[0]
# ~\~ begin <<lit/paranoodles.md|import-dask>>[0]
from dask import delayed
# ~\~ end
import numpy as np

from pintFoam.parareal.harmonic_oscillator import \
    ( harmonic_oscillator, underdamped_solution )
from pintFoam.parareal.forward_euler import \
    ( forward_euler )
from pintFoam.parareal.tabulate_solution import \
    ( tabulate )
from pintFoam.parareal.parareal import \
    ( parareal )


@delayed
def gather(*args):
    return list(args)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[1]
omega_0 = 1.0
zeta = 0.5
f = harmonic_oscillator(omega_0, zeta)
t = np.linspace(0.0, 15.0, 4)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[2]
h = 0.01

@delayed
def fine(x, t_0, t_1):
    return iterate_solution(forward_euler(f), h)(x, t_0, t_1)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[3]
y_euler = gather(
    *tabulate(fine, [1.0, 0.0], t))
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[4]
def paint(node, name):
    if name == "coarse":
        node.attr["fillcolor"] = "#cccccc"
    elif name == "fine":
        node.attr["fillcolor"] = "#88ff88"
    else:
        node.attr["fillcolor"] = "#ffffff"

y_euler.visualize("seq-graph.svg")
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[5]
@delayed
def coarse(x, t_0, t_1):
    return forward_euler(f)(x, t_0, t_1)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[6]
y_first = gather(*tabulate(coarse, [1.0, 0.0], t))
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[7]
y_parareal = gather(*parareal(coarse, fine)(y_first, t))
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|daskify>>[8]
y_parallel.visualize("parareal-graph.svg")
# ~\~ end
# ~\~ end
