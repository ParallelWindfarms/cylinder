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

# Interface with ParaNoodles
We need to define the following:

* `Vector`
* fine `Solution`
* coarse `Solution`
* coarsening operator
* refinement operator (interpolation)

The last two steps will require the use of the `mapFields` utility in OpenFOAM and may require some tweaking to work out.

- [ ] figure out how to work `mapFields`, and make this scriptable from Python.

## Vector

The abstract `Vector`, defined below, represents any single state in the simulation. It consists of a `RunDirectory` and a time-frame.

``` {.python file=pintFoam/vector.py}
from __future__ import annotations

import operator
import mmap

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from shutil import copytree, rmtree   # , copy
from typing import List, Optional

from byteparsing import parse_bytes, foam_file
# from .utils import pushd

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile  # type: ignore
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory      # type: ignore

<<base-case>>
<<pintfoam-vector>>
```

### Base case
We will operate on a `Vector` the same way everything is done in OpenFOAM, that is:

1. Copy-paste a case (known as the base case)
2. Edit the copy with new simulation parameters
3. Run the simulation

This is why for every `Vector` we define a `BaseCase` that is used to generate new vectors. The `BaseCase` should have only one time directory containing the initial conditions, namely `0`. The simulation generates new folders containing the data corresponding to different times. The time is coded, somewhat uncomfortably, in the directory name (`0.01`, `0.02`, and so on).

The class `Vector` takes care of all those details.

``` {.python #base-case}
@dataclass
class BaseCase:
    """Base case is a cleaned version of the system. If it contains any fields,
    it will only be the `0` time. Any field that is copied for manipulation will
    do so on top of an available base case in the `0` slot."""
    root: Path
    case: str
    fields: Optional[List[str]] = None

    @property
    def path(self):
        return self.root / self.case

    def new_vector(self, name=None):
        """Creates new `Vector` using this base case."""
        new_case = name or uuid4().hex
        new_path = self.root / new_case
        if not new_path.exists():
            copytree(self.path, new_path)
        return Vector(self, new_case, "0")

    def all_vector_paths(self):
        """Iterates all sub-directories in the root."""
        return (x for x in self.root.iterdir()
                if x.is_dir() and x.name != self.case)

    def clean(self):
        """Deletes all vectors of this base-case."""
        for path in self.all_vector_paths():
            rmtree(path)
```

In our implementation, if no name is given to a new vector, a random one is generated.

### Retrieving files and time directories
Note that the `BaseCase` has a property `path`. The same property will be defined in `Vector`. We can use this common property to retrieve a `SolutionDirectory`, `ParameterFile` or `TimeDirectory`.

- [ ] These are PyFoam routines that may need to be replaced

``` {.python #pintfoam-vector}
def solution_directory(case):
    return SolutionDirectory(case.path)

def parameter_file(case, relative_path):
    return ParsedParameterFile(case.path / relative_path)

def time_directory(case):
    return solution_directory(case)[case.time]


def get_times(path):
    """Get all the snapshots in a case, sorted on floating point value."""
    def isfloat(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    return sorted(
        [s.name for s in path.iterdir() if isfloat(s.name)],
        key=float)
```

### Vector

``` {.python #pintfoam-vector}
@dataclass
class Vector:
    base: BaseCase
    case: str
    time: str

    <<pintfoam-vector-properties>>
    <<pintfoam-vector-clone>>
    <<pintfoam-vector-operate>>
    <<pintfoam-vector-operators>>
```

From a vector we can extract a file path pointing to the specified time slot, list the containing files and read out `internalField` from any of those files.

- [ ] `files` property would work different with Adios.
- [ ] port `internalField` method to Adios.

``` {.python #pintfoam-vector-properties}
@property
def path(self):
    """Case path, i.e. the path containing `system`, `constant` and snapshots."""
    return self.base.root / self.case

@property
def fields(self):
    """All fields relevant to this base case."""
    return self.base.fields

@property
def dirname(self):
    """The path of this snapshot."""
    return self.path / self.time

def all_times(self):
    """Get all available times, in order."""
    return [Vector(self.base, self.case, t)
            for t in get_times(self.path)]

@contextmanager
def mmap_data(self, field):
    """Context manager that yields a **mutable** reference to the data contained
    in this snapshot. Mutations done to this array are mmapped to the disk directly."""
    f = (self.dirname / field).open(mode="r+b")
    with mmap.mmap(f.fileno(), 0) as mm:
        content = parse_bytes(foam_file, mm)
        yield content["data"]["internalField"]
```

We clone a vector by creating a new vector and copying the internal fields.

- [ ] using Adios the location of a time-frame is different, copy `adiosData/{time}.bp*` instead

``` {.python #pintfoam-vector-clone}
def clone(self):
    """Clone this vector to a new one. The clone only contains this single snapshot."""
    x = self.base.new_vector()
    x.time = self.time
    rmtree(x.dirname, ignore_errors=True)
    copytree(self.dirname, x.dirname)
    return x
```

In order to apply the parareal algorithm to our vectors (or indeed, any other algorithm worth that name), we need to define how to operate with them. Particularly, we'll need to implement:

- Vector addition and subtraction (as we'll need to sum and subtract the results of applying the coarse and fine integrators)
- Vector scaling (as the integrators involve scaling with the inverse of the step)

In order to achieve this, first we'll write generic recipes for **any** operation between vectors and **any** operation between a scalar and a vector:

``` {.python #pintfoam-vector-operate}
def zip_with(self, other: Vector, op) -> Vector:
    x = self.clone()
    <<copy-attrs-and-bounds>>

    for f in self.fields:
        with x.mmap_data(f) as a, other.mmap_data(f) as b:
            a[:] = op(a, b)
    return x

def map(self, f) -> Vector:
    x = self.clone()

    for f in self.fields:
        with x.mmap_data(f) as a:
            a[:] = f(a)
    return x
```

<<<<<<< HEAD
``` {.python #copy-attrs-and-bounds}
# We're back to mutating a clone, so no copying of attrs needed.
```
=======
_The conditional structures in the chunk above are due to the fact that uniform and non-uniform fields are stored in not mutually-compatible ways, forcing us to operate differently with them._
>>>>>>> master

We now have the tools to define vector addition, subtraction and scaling.

``` {.python #pintfoam-vector-operators}
def __sub__(self, other: Vector) -> Vector:
    return self.zip_with(other, operator.sub)

def __add__(self, other: Vector) -> Vector:
    return self.zip_with(other, operator.add)

def __mul__(self, scale: float) -> Vector:
    return self.map(lambda x: x * scale)
```

In the code chunk above we used the so-called magic methods. If we use a minus sign to subtract two vectors, the method `__sub__` is being executed under the hood.

### `setFields` utility

We may want to call `setFields` on our `Vector` to setup some test cases.

- [ ] port to Adios
- [ ] add doc-string

``` {.python #pintfoam-set-fields}
def set_fields(v, *, defaultFieldValues, regions):
    x = parameter_file(v, "system/setFieldsDict")
    x['defaultFieldValues'] = defaultFieldValues
    x['regions'] = regions
    x.writeFile()
    subprocess.run("setFields", cwd=v.path, check=True)
```

## Solution

Remember, the definition of a `Solution`,

``` {.python}
Solution = Callable[[Vector, float, float], Vector]
```

meaning, we write a function taking a current state `Vector`, the time *now*, and the *target* time, returning a new `Vector`.


``` {.python file=pintFoam/solution.py}
import subprocess
import math
from typing import Optional, Union

from .vector import (BaseCase, Vector, parameter_file, get_times)

def block_mesh(case: BaseCase):
    subprocess.run("blockMesh", cwd=case.path, check=True)

<<pintfoam-set-fields>>
<<pintfoam-epsilon>>
<<pintfoam-solution>>
```

The solver will write directories with floating-point valued names. This is a very bad idea by the folks at OpenFOAM, but it is one we'll have to live with. Suppose you have a time-step of $0.1$, what will be the names of the directories if you integrate from $0$ to $0.5$?

``` {.python session=0}
[x * 0.1 for x in range(6)]
```

In Python 3.7, this gives `[0.0, 0.1, 0.2, 0.30000000000000004, 0.4, 0.5]`. Surely, if you give a time-step of $0.1$ to OpenFOAM, it will create a directory named `0.3` instead. We'll define the constant `epsilon` to aid us in identifying the correct state directory given a floating-point time.

``` {.python #pintfoam-epsilon}
epsilon = 1e-6
```

Our solution depends on the solver chosen and the given time-step:

``` {.python #pintfoam-solution}
def foam(solver: str, dt: float, x: Vector, t_0: float, t_1: float,
         write_interval: Optional[Union[int,float]] = None) -> Vector:
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
    <<pintfoam-solution-function>>
```

The solver clones a new vector, sets the `controlDict`, runs the solver and then creates a new vector representing the last time slice.

``` {.python #pintfoam-solution-function}
assert abs(float(x.time) - t_0) < epsilon, f"Times should match: {t_0} != {x.time}."
y = x.clone()
write_interval = write_interval or (1 if solver == "scalarTransportFoam" else dt)
<<set-control-dict>>
<<run-solver>>
<<return-result>>
```

### `controlDict`

- [x] check if this is enough to have Adios 'restart' from the correct time

``` {.python #set-control-dict}
controlDict = parameter_file(y, "system/controlDict")
controlDict.content['startFrom'] = "latestTime"
controlDict.content['startTime'] = t_0
controlDict.content['endTime'] = t_1
controlDict.content['deltaT'] = dt
controlDict.content['writeInterval'] = write_interval
controlDict.writeFile()
```

### Run solver

- [ ] Change `Execution.AnalyzedRunner` to self-coded `subprocess.run` type of operation.

``` {.python #run-solver}
subprocess.run(solver, cwd=y.path, check=True)

```

### Return result

``` {.python #return-result}
t1_str = get_times(y.path)[-1]
return Vector(y.base, y.case, t1_str)
```

# Running Parareal

``` {.python file=run.py}
import numpy as np

import noodles
from noodles.draw_workflow import draw_workflow
from noodles.run.threading.vanilla import run_parallel
from noodles.run.process import run_process
from noodles.run.single.vanilla import run_single
from noodles.display.simple_nc import Display

from noodles import serial
from paranoodles import tabulate, parareal

from pintFoam.vector import BaseCase
from pintFoam.run import (coarse, fine, registry)
from pathlib import Path


def paint(node, name):
    if name == "coarse":
        node.attr["fillcolor"] = "#cccccc"
    elif name == "fine":
        node.attr["fillcolor"] = "#88ff88"
    else:
        node.attr["fillcolor"] = "#ffffff"

if __name__ == "__main__":
    t = np.linspace(0.0, 1.0, 6)
    base_case = BaseCase(Path("data/c1").resolve(), "baseCase")

    y = noodles.gather(*tabulate(coarse, base_case.new_vector(), t))
    s = noodles.gather(*parareal(fine, coarse)(y, t))

    # draw_workflow("wf.svg", noodles.get_workflow(s), paint)
    result = run_process(s, n_processes=4, registry=registry, verbose=True)
    # result = run_single(s)

    print(result)
# base_case.clean()
```

- [ ] update Noodles registry to work with Adios files.

``` {.python file=pintFoam/run.py}
import noodles   # type: ignore
from noodles import serial

from .solution import foam

@noodles.schedule
def fine(x, t_0, t_1):
    return foam("icoFoam", 0.05, x, t_0, t_1)

@noodles.schedule
def coarse(x, t_0, t_1):
    return foam("icoFoam", 0.2, x, t_0, t_1)

def registry():
    return serial.base() + serial.numpy()
```

# The User script
As the final bit, the user should write a (minimal) script for running the simulation. Here we write an example script in the `data` folder. There should be no reusable parts in this script, or they should go into either the `paranoodles` or `pintFoam` module.

Time for a bit of wishful programming

``` {.python file=data/run.py}
from pathlib import Path
import numpy as np
from paranoodles import (schedule, run, parareal, tabulate)
from pintFoam import (BaseCase, foam, block_mesh, serial)


case = BaseCase(Path("c1"), "baseCase")
block_mesh(case)


@schedule
def fine(x, t_0, t_1):
    return foam("icoFoam", 0.05, x, t_0, t_1)


@schedule
def coarse(x, t_0, t_1):
    return foam("icoFoam", 0.2, x, t_0, t_1)


times = np.linspace(0.0, 10.0, 100)
init = foam("icoFoam", 0.05, case.new_vector(), 0.0, 0.0)
tabulate(parareal(coarse, fine), init, times)
```

# Appendix A: Utils

``` {.python file=pintFoam/utils.py}
<<push-dir>>
```

## Cleaning up

``` {.python file=pintFoam/clean.py}
import argh  # type:ignore
from pathlib import Path
from .vector import BaseCase


@argh.arg("target", help="target path to clean")
@argh.arg("--base_case", help="name of the base-case")
def main(target: Path, base_case: str = "baseCase"):
    BaseCase(Path(target), base_case).clean()


if __name__ == "__main__":
    argh.dispatch_command(main)
```

## `pushd`

I haven't been able (with simple attempts) to run a case outside the definition directory. Similar to the `pushd` bash command, I define a little utility in Python:

``` {.python #push-dir}
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Union

@contextmanager
def pushd(path: Union[str, Path]):
    """Context manager to change directory to given path,
    and get back to current dir at exit."""
    prev = Path.cwd()
    os.chdir(path)

    try:
        yield
    finally:
        os.chdir(prev)
```
