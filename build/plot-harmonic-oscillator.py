# ~\~ language=Python filename=build/plot-harmonic-oscillator.py
# ~\~ begin <<lit/parareal.md|build/plot-harmonic-oscillator.py>>[init]
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
plt.plot(t, y_exact[:,0], color='orangered', label="exact")
plt.plot(t, y_euler[:,1], color='slateblue', linestyle=':')
plt.plot(t, y_exact[:,1], color='orangered', linestyle=':')
plt.legend()
plt.savefig("docs/img/harmonic.svg")
# ~\~ end
