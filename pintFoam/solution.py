## ------ language="Python" file="pintFoam/solution.py"
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.StandardLogAnalyzer import StandardLogAnalyzer

from .vector import (Vector, parameter_file, solution_directory)

## ------ begin <<pintfoam-epsilon>>[0]
epsilon = 1e-6
## ------ end
## ------ begin <<pintfoam-solution>>[0]
def solution(solver: str, dt: float):
    ## ------ begin <<pintfoam-solution-function>>[0]
    def f(x: Vector, t_0: float, t_1: float):
        assert abs(float(x.time) - t_0) < epsilon, "Times should match."
        y = x.clone()
        ## ------ begin <<set-control-dict>>[0]
        controlDict = parameter_file(y, "system/controlDict")
        controlDict.content['startTime'] = t_0
        controlDict.content['endTime'] = t_1
        controlDict.content['deltaT'] = dt
        controlDict.writeFile()
        ## ------ end
        ## ------ begin <<run-solver>>[0]
        run = AnalyzedRunner(StandardLogAnalyzer(), argv=[solver], silent=True)
        run.start()
        ## ------ end
        ## ------ begin <<return-result>>[0]
        sd = solution_directory(y)
        t1_str = sd.times[-1]
        return Vector(y.base, y.case, t1_str)
        ## ------ end
    ## ------ end
    return f
## ------ end
## ------ end
