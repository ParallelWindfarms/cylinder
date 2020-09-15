# ~\~ language=Python filename=pintFoam/solution.py
# ~\~ begin <<lit/cylinder.md|pintFoam/solution.py>>[0]
# from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
# from PyFoam.LogAnalysis.StandardLogAnalyzer import StandardLogAnalyzer
import subprocess

from .vector import (Vector, parameter_file, solution_directory)
from .utils import pushd

# ~\~ begin <<lit/cylinder.md|pintfoam-epsilon>>[0]
epsilon = 1e-6
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-solution>>[0]
def foam(solver: str, dt: float, x: Vector, t_0: float, t_1: float) -> Vector:
    # ~\~ begin <<lit/cylinder.md|pintfoam-solution-function>>[0]
    assert abs(float(x.time) - t_0) < epsilon, f"Times should match: {t_0} != {x.time}."
    y = x.clone()
    # ~\~ begin <<lit/cylinder.md|set-control-dict>>[0]
    controlDict = parameter_file(y, "system/controlDict")
    controlDict.content['startTime'] = t_0
    controlDict.content['endTime'] = t_1
    controlDict.content['deltaT'] = dt
    controlDict.content['writeInterval'] = 1
    controlDict.writeFile()
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|run-solver>>[0]
    subprocess.run(solver, cwd=y.path, check=True)

    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|return-result>>[0]
    sd = solution_directory(y)
    t1_str = sd.times[-1]
    return Vector(y.base, y.case, t1_str)
    # ~\~ end
    # ~\~ end
# ~\~ end
# ~\~ end
