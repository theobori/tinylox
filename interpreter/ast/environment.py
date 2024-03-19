"""environment module"""

from typing import Any, Self

from ..scanner.token import Token
from ..error.error import RuntimeErrorL

class Environment:
    """
        Represents a variables environment
    """
    
    def __init__(self, enclosing: Self=None):
        self.values = {}
        self.enclosing = enclosing
    
    def get(self, name: Token) -> Any:
        """
            Resolves a variable
        """
        
        value = self.values.get(name.lexeme)
        
        if value != None:
            return value

        if self.enclosing != None:
            return self.enclosing.get(name)
    
        raise RuntimeErrorL(
            name,
            "Undefined variable '" + name.lexeme + "'"
        )
    
    def __ancestor(self, distance: int) -> Self:
        """
            Return an environement at a given position
        """
        
        environment = self
        
        for _ in range(distance):
            environment = environment.enclosing
        
        return environment
    
    def get_at(self, distance: int, name: str) -> Any:
        """
            Return a value from an environment at distance `distance`
        """
        
        return self.__ancestor(distance).values.get(name)
    
    def assign(self, name: Token, value: Any):
        """
            Update a variable value
        """
        
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return
        
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeErrorL(
            name,
            "Undefined variable '" + name.lexeme + "'"
        )
    
    def assign_at(self, distance: int, name: Token, value: Any):
        """
            Update a variable on an environent at a certain distance
        """
        
        self.__ancestor(distance).values[name] = value
    
    def define(self, name: str, value: Any):
        """
            Add a variable with its value
        """
        
        self.values[name] = value
