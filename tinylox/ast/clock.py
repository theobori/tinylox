"""clock native function module"""

from time import time
from typing import Any, List

from .callable import LoxCallable


class Clock(LoxCallable):
    """
    Clock native function
    """

    def __call__(self, interpreter: object, arguments: List[Any]) -> Any:
        return time()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<native function>"
