"""function module"""

from typing import List, Any

from .callable import LoxCallable
from .expr import FunctionStatement
from .environment import Environment
from ._return import Return


class LoxFunction(LoxCallable):
    """
    Function expression back end
    """

    def __init__(self, declaration: FunctionStatement, closures: Environment):
        self.__declaration = declaration
        self.__closures = closures

    def __call__(self, interpreter: object, arguments: List[Any]) -> Any:
        environement = Environment(self.__closures)

        for argument, declaration in zip(arguments, self.__declaration.parameters):
            environement.define(declaration.lexeme, argument)

        try:
            interpreter.execute_block(self.__declaration.body, environement)
        except Return as error:
            return error.value

        return None

    def __str__(self) -> str:
        return "<fn " + self.__declaration.name.lexeme + ">"

    def arity(self) -> int:
        return len(self.__declaration.parameters)
