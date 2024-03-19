"""return module"""

from typing import Any

class Return(RuntimeError):
    """
        Return exception
    """
    
    def __init__(self, value: Any):
        self.__value = value

    @property
    def value(self) -> Any:
        return self.__value
