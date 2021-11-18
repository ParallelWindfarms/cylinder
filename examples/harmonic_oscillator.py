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

# ~\~ begin <<lit/paranoodles.md|noodlify>>[0]
# ~\~ begin <<lit/paranoodles.md|import-noodles>>[0]
import noodles
# ~\~ end
import numpy as np
from noodles.draw_workflow import draw_workflow

from parareal.harmonic_oscillator import \
    ( harmonic_oscillator, underdamped_solution )
from parareal.forward_euler import \
    ( forward_euler )
from parareal.tabulate_solution import \
    ( tabulate )
from parareal.parareal import \
    ( parareal )
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[1]
omega_0 = 1.0
zeta = 0.5
f = harmonic_oscillator(omega_0, zeta)
t = np.linspace(0.0, 15.0, 4)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[2]
h = 0.01

@noodles.schedule
def fine(x, t_0, t_1):
    return iterate_solution(forward_euler(f), h)(x, t_0, t_1)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[3]
y_euler = noodles.gather(
    *tabulate(fine, [1.0, 0.0], t))
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[4]
def paint(node, name):
    if name == "coarse":
        node.attr["fillcolor"] = "#cccccc"
    elif name == "fine":
        node.attr["fillcolor"] = "#88ff88"
    else:
        node.attr["fillcolor"] = "#ffffff"

draw_workflow('seq-graph.svg', noodles.get_workflow(y_euler), paint)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[5]
@noodles.schedule
def coarse(x, t_0, t_1):
    return forward_euler(f)(x, t_0, t_1)
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[6]
y_first = noodles.gather(*tabulate(coarse, [1.0, 0.0], t))
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[7]
y_parareal = noodles.gather(*parareal(coarse, fine)(y_first, t))
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|noodlify>>[8]
draw_workflow('parareal-graph.svg', noodles.get_workflow(y_parareal), paint)
# ~\~ end
# ~\~ end
