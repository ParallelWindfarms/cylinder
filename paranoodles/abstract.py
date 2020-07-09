# ~\~ language=Python filename=paranoodles/abstract.py
# ~\~ begin <<lit/paranoodles.md|paranoodles/abstract.py>>[0]
from __future__ import annotations  # enable self-reference in type annotations
from typing import Callable
from abc import (ABC, abstractmethod)

# ~\~ begin <<lit/paranoodles.md|abstract-types>>[0]
class Vector(ABC):
    """Abstract base class for state variable of a problem.
    This should support simple arithmatic operations."""
    @abstractmethod
    def __add__(self, other: Vector) -> Vector:
        """Summation of two result vectors."""
        pass

    @abstractmethod
    def __sub__(self, other: Vector) -> Vector:
        """Difference between two result vectors."""
        pass

    @abstractmethod
    def __mul__(self, other: float) -> Vector:
        """Scale vector with scalar."""
        pass

    def __rmul__(self, other: float) -> Vector:
        return self * other
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|abstract-types>>[1]
Problem = Callable[[Vector, float], Vector]
# ~\~ end
# ~\~ begin <<lit/paranoodles.md|abstract-types>>[2]
Solution = Callable[[Vector, float, float], Vector]
# ~\~ end
# ~\~ end
