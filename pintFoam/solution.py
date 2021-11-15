# ~\~ language=Python filename=pintFoam/solution.py
# ~\~ begin <<lit/cylinder.md|pintFoam/solution.py>>[0]
import subprocess
import math
from typing import Optional, Union

from .vector import (BaseCase, Vector, parameter_file, get_times)

def block_mesh(case: BaseCase):
    subprocess.run("blockMesh", cwd=case.path, check=True)

def map_fields(source: Vector, target: BaseCase, consistent=True, map_method=None) -> Vector:
    """
    Valid arguments for `map_method`: mapNearest, interpolate, cellPointInterpolate
    """
    result = target.new_vector()
    result.time = source.time
    arg_lst = ["mapFields"]
    if consistent:
        arg_lst.append("-consistent")
    if map_method is not None:
        arg_lst.extend(["-mapMethod", map_method])
    arg_lst.extend(["-sourceTime", source.time, source.path.resolve()])
    subprocess.run(arg_lst, cwd=result.path, check=True)
    (result.path / "0").rename(result.dirname)
    return result

# ~\~ begin <<lit/cylinder.md|pintfoam-set-fields>>[0]
def set_fields(v, *, default_field_values, regions):
    x = parameter_file(v, "system/setFieldsDict")
    x['defaultFieldValues'] = default_field_values
    x['regions'] = regions
    x.writeFile()
    subprocess.run("setFields", cwd=v.path, check=True)
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-epsilon>>[0]
epsilon = 1e-6
# ~\~ end
# ~\~ begin <<lit/cylinder.md|pintfoam-solution>>[0]
def foam(solver: str, dt: float, x: Vector, t_0: float, t_1: float,
         write_interval: Optional[Union[int,float]] = None,
         job_name: Optional[str] = None) -> Vector:
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
    y = x.clone(job_name)
    write_interval = write_interval or (1 if solver == "scalarTransportFoam" else dt)
    # ~\~ begin <<lit/cylinder.md|set-control-dict>>[0]
    for i in range(5):   # this sometimes fails, so we try a few times, maybe disk sync issue?
        try:
            controlDict = parameter_file(y, "system/controlDict")
            controlDict.content['startFrom'] = "latestTime"
            controlDict.content['startTime'] = t_0
            controlDict.content['endTime'] = t_1
            controlDict.content['deltaT'] = dt
            controlDict.content['writeInterval'] = write_interval
            controlDict.writeFile()
            break
        except Exception as e:
            exception = e
    else:
        raise exception

    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|run-solver>>[0]
    with open(y.path / "log.stdout", "w") as logfile, \
         open(y.path / "log.stderr", "w") as errfile:
        subprocess.run(solver, cwd=y.path, check=True, stdout=logfile, stderr=errfile)

    # ~\~ end
    # ~\~ begin <<lit/cylinder.md|return-result>>[0]
    t1_str = get_times(y.path)[-1]
    return Vector(y.base, y.case, t1_str)
    # ~\~ end
    # ~\~ end
# ~\~ end
# ~\~ end
