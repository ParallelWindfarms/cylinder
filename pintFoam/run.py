## ------ language="Python" file="pintFoam/run.py"
import noodles
from noodles.draw_workflow import draw_workflow

from paranoodles.parareal import \
    ( parareal )

from .vector import BaseCase
from .solution import foam

@noodles.schedule
def fine(x, t_0, t_1):
    return foam("icoFoam", 0.05, x, t_0, t_1)

@noodles.schedule
def coarse(x, t_0, t_1):
    return foam("icoFoam", 0.2, x, t_0, t_1)

def paint(node, name):
    if name == "coarse":
        node.attr["fillcolor"] = "#cccccc"
    elif name == "fine":
        node.attr["fillcolor"] = "#88ff88"
    else:
        node.attr["fillcolor"] = "#ffffff"
## ------ end
