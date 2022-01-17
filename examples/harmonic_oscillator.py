# ~\~ language=Python filename=examples/harmonic_oscillator.py
# ~\~ begin <<lit/parareal.md|examples/harmonic_oscillator.py>>[0]
# ~\~ begin <<lit/parareal.md|plot-harmonic-oscillator>>[0]
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

# ~\~ begin <<lit/parareal.md|daskify>>[0]
# ~\~ begin <<lit/parareal.md|import-dask>>[0]
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


attrs = {}

def green(f):
    def greened(*args):
        node = f(*args)
        attrs[node.key] = {"fillcolor": "#8888cc", "style": "filled"}
        return node
    return greened

@delayed
def gather(*args):
    return list(args)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[1]
omega_0 = 1.0
zeta = 0.5
f = harmonic_oscillator(omega_0, zeta)
t = np.linspace(0.0, 15.0, 4)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[2]
h = 0.01

@green
@delayed
def fine(x, t_0, t_1):
    return iterate_solution(forward_euler(f), h)(x, t_0, t_1)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[3]
y_euler = tabulate(fine, [1.0, 0.0], t)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[4]
gather(*y_euler).visualize("seq-graph.svg", rankdir="LR", data_attributes=attrs)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[5]
@delayed
def coarse(x, t_0, t_1):
    return forward_euler(f)(x, t_0, t_1)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[6]
y_first = tabulate(coarse, [1.0, 0.0], t)
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[7]
y_parareal = gather(*parareal(coarse, fine)(y_first, t))
# ~\~ end
# ~\~ begin <<lit/parareal.md|daskify>>[8]
y_parareal.visualize("parareal-graph.pdf", rankdir="LR", data_attributes=attrs)
# ~\~ end
# ~\~ end
