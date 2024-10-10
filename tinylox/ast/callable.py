"""callable module"""

from typing import Any, List


class LoxCallable:
    """
    Callable expression back end
    """

    def __call__(self, interpreter: object, arguments: List[Any]) -> Any:
        raise Exception("Not implemented")

    def arity(self) -> int:
        """
        Get the expected arguments amount
        """

        raise Exception("Not implemented")
