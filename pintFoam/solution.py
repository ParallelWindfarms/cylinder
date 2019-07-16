## ------ language="Python" file="pintFoam/solution.py"
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.StandardLogAnalyzer import StandardLogAnalyzer

from .vector import (Vector, parameter_file, solution_directory)
from .utils import pushd

## ------ begin <<pintfoam-epsilon>>[0]
epsilon = 1e-6
## ------ end
## ------ begin <<pintfoam-solution>>[0]
def foam(solver: str, dt: float, x: Vector, t_0: float, t_1: float):
    ## ------ begin <<pintfoam-solution-function>>[0]
    assert abs(float(x.time) - t_0) < epsilon, f"Times should match: {t_0} != {x.time}."
    y = x.clone()
    ## ------ begin <<set-control-dict>>[0]
    controlDict = parameter_file(y, "system/controlDict")
    controlDict.content['startTime'] = t_0
    controlDict.content['endTime'] = t_1
    controlDict.content['deltaT'] = dt
    controlDict.content['writeInterval'] = dt
    controlDict.writeFile()
    ## ------ end
    ## ------ begin <<run-solver>>[0]
    with pushd(y.path):
        run = AnalyzedRunner(StandardLogAnalyzer(), argv=[solver], silent=True)
        run.start()
    ## ------ end
    ## ------ begin <<return-result>>[0]
    sd = solution_directory(y)
    t1_str = sd.times[-1]
    return Vector(y.base, y.case, t1_str)
    ## ------ end
    ## ------ end
## ------ end
## ------ end
