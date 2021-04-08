# ~\~ language=Python filename=pintFoam/solution.py
# ~\~ begin <<lit/cylinder.md|pintFoam/solution.py>>[0]
import subprocess
import math
from typing import Optional

from .vector import (BaseCase, Vector, parameter_file, get_times)

def run_block_mesh(case: BaseCase):
    subprocess.run("blockMesh", cwd=case.path, check=True)

# ~\~ begin <<lit/cylinder.md|pintfoam-set-fields>>[0]
def setFields(v, *, defaultFieldValues, regions):
    x = parameter_file(v, "system/setFieldsDict")
    x['defaultFieldValues'] = defaultFieldValues
    x['regions'] = regions
    x.writeFile()
    subprocess.run("setFields", cwd=v.path, check=True)
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-epsilon>>[0]
epsilon = 1e-6
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-solution>>[0]
def foam(solver: str, dt: float, x: Vector, t_0: float, t_1: float,
         write_interval: Optional[int] = None) -> Vector:
    """Call an OpenFOAM code.

    Args:
        solver: The name of the solver (e.g. "icoFoam", "scalarTransportFoam" etc.)
        dt:     deltaT parameter
        x:      initial state
        t_0:    startTime (should match that in initial state)
        t_1:    endTime
        write_interval: if not given, this is computed so that only the endTime
                is written.

    Returns:
        The `Vector` representing the end state.
    """
    # ~\~ begin <<lit/cylinder.md|pintfoam-solution-function>>[0]
    assert abs(float(x.time) - t_0) < epsilon, f"Times should match: {t_0} != {x.time}."
    y = x.clone()
    write_interval = write_interval or dt
    # ~\~ begin <<lit/cylinder.md|set-control-dict>>[0]
    controlDict = parameter_file(y, "system/controlDict")
    controlDict.content['startFrom'] = "latestTime"
    controlDict.content['startTime'] = t_0
    controlDict.content['endTime'] = t_1
    controlDict.content['deltaT'] = dt
    controlDict.content['writeInterval'] = write_interval
    controlDict.writeFile()
    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|run-solver>>[0]
    subprocess.run(solver, cwd=y.path, check=True)

    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|return-result>>[0]
    t1_str = get_times(y.path)[-1]
    return Vector(y.base, y.case, t1_str)
    # ~\~ end
    # ~\~ end
# ~\~ end
# ~\~ end
