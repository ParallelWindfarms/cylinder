# PyFOAM

PyFOAM is not so well documented. For our application we'd like to do two things: modify the run-directory and run `icoFoam`. We'll start with the following modules:

- `PyFoam.Execution`
- `PyFoam.RunDictionary`
- `PyFoam.LogAnalysis`

The PyFAOM module comes with a lot of tools to analyse the logs that are being created so fanatically by the solvers.

## Running `elbow` example

To run the "elbow" example:

``` {.python #elbow-example}
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.StandardLogAnalyzer import StandardLogAnalyzer
```

The `AnalyzedRunner` runs a command and sends the results to an `Analyzer` object, all found in the `PyFoam.LogAnalysis` module, in this case the `StandardLogAnalyzer`.

``` {.python session=0}
import numpy as np
from pathlib import Path
from pintFoam.utils import pushd

path = Path("./elbow").absolute()
solver = "icoFoam"

with pushd(path):
    run = AnalyzedRunner(StandardLogAnalyzer(), argv=[solver], silent=True)
    run.start()
```

### Get results

All access to files goes through the `PyFoam.RunDictionary` submodule.

``` {.python session=0}
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
dire = SolutionDirectory(path)
```

Query for the time slices,

``` {.python session=0}
dire.times
```

And read some result data,

``` {.python session=0 clip-output=4}
p = dire[10]['p'].getContent()['internalField']
np.array(p.val)
```

### Clear results

``` {.python session=0}
dire.clearResults()
```

### Change integration interval and time step

We'll now access the `controlDict` file.

``` {.python session=0}
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
controlDict = ParsedParameterFile(dire.controlDict())
controlDict.content
```

change the end time

``` {.python session=0}
controlDict['endTime'] = 20
controlDict.writeFile()
```

## Why we're not using PyFOAM for running
PyFOAM seems to have global state somewhere. Running multiple sessions in parallel is not working.

