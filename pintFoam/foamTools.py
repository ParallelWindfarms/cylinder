# ~\~ language=Python filename=pintFoam/foamTools.py
# ~\~ begin <<lit/cylinder.md|pintFoam/foamTools.py>>[0]
from dataclasses import dataclass
from typing import Callable

from .utils import decorator

Stub = Callable[[], None]


@decorator
@dataclass
class Tool:
    _func: Stub
    command: str
    arguments: list[str]



# ~\~ end
