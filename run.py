## ------ language="Python" file="run.py"
import numpy as np

import noodles
from noodles.draw_workflow import draw_workflow
from noodles.run.threading.vanilla import run_parallel
from noodles.run.process import run_process
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
    result = run_process(s, n_processes=4, registry=registry)

    print(result)
# base_case.clean()
## ------ end
