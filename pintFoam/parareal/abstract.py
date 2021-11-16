# ~\~ language=Python filename=pintFoam/parareal/abstract.py
# ~\~ begin <<lit/paranoodles.md|pintFoam/parareal/abstract.py>>[0]
from __future__ import annotations  # enable self-reference in type annotations
from typing import (Callable, Protocol, TypeVar)

# ~\~ begin <<lit/paranoodles.md|abstract-types>>[0]
TVector = TypeVar("TVector", bound="Vector")

class Vector(Protocol):
    def __add__(self: TVector, other: TVector) -> TVector:
        ...

    def __sub__(self: TVector, other: TVector) -> TVector:
        ...

    def __mul__(self: TVector, other: float) -> TVector:
        ...

    def __rmul__(self: TVector, other: float) -> TVector:
        ...

# ~\~ end
# ~\~ begin <<lit/paranoodles.md|abstract-types>>[1]
Problem = Callable[[TVector, float], TVector]
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|abstract-types>>[2]
Solution = Callable[[TVector, float, float], TVector]
# ~\~ end
Mapping = Callable[[TVector], TVector]
# ~\~ end
