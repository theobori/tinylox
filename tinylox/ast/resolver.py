"""resolver module"""

from typing import Any, List
from enum import Enum

from .interpreter import Interpreter
from ..scanner.token import Token
from .expr import (
    Visitor,
    Statement,
    Expr,
    BlockStatement,
    VarStatement,
    Variable,
    Assign,
    FunctionStatement,
    ExpressionStatement,
    IfStatement,
    PrintStatement,
    ReturnStatement,
    WhileStatement,
    Binary,
    Call,
    Grouping,
    Literal,
    Logical,
    Unary,
)
from ..error.error import Error


class FunctionKind(Enum):
    NONE = "None"
    FUNCTION = "Function"


class Resolver(Visitor):
    """
    AST variable resolution
    """

    def __init__(self, interpreter: Interpreter):
        self.__interpreter = interpreter
        self.__scopes = []

        self.__current_function = FunctionKind.NONE

    def resolve_expression(self, expr: Expr):
        """
        Resolve expression
        """

        expr.accept(self)

    def resolve_statement(self, statement: Statement):
        """
        Resolve statement
        """

        statement.accept(self)

    def resolve_statements(self, statements: List[Statement]):
        """
        Resolve statements
        """

        for statement in statements:
            self.resolve_statement(statement)

    def __begin_scope(self):
        """
        Add a scope to the stack
        """

        self.__scopes.append({})

    def __end_scope(self):
        """
        Remove a scope from the stack
        """

        self.__scopes.pop()

    def visit_block_statement(self, statement: BlockStatement) -> Any:
        self.__begin_scope()
        self.resolve_statements(statement.statements)
        self.__end_scope()

    def __declare(self, name: Token):
        """
        Set the identifier to the "declared" state
        """

        if not self.__scopes:
            return

        if name.lexeme in self.__scopes[-1].keys():
            Error.error_token(name, "Already a variable with this name in this scope")

        self.__scopes[-1][name.lexeme] = False

    def __define(self, name: Token):
        """
        Set the identifier to the "defined" state
        """

        if not self.__scopes:
            return

        self.__scopes[-1][name.lexeme] = True

    def __resolve_expression_local(self, expr: Expr, name: Token):
        """
        If None is returned, the variable is inside the global scope,
        else, it returns the scope position
        """

        scopes = self.__scopes[::-1]

        for i, scope in enumerate(scopes):
            if name.lexeme in scope.keys():
                self.__interpreter.resolve_expr(expr, i)
                return

    def visit_variable_expr(self, expr: Variable) -> Any:
        if self.__scopes and not self.__scopes[-1].get(expr.name.lexeme):
            Error.error_token(
                expr.name, "Can't read local variable in its own initializer"
            )

        self.__resolve_expression_local(expr, expr.name)

    def visit_var_statement(self, statement: VarStatement) -> Any:
        self.__declare(statement.name)

        if statement.initializer is not None:
            self.resolve_expression(statement.initializer)

        self.__define(statement.name)

    def visit_assign_expr(self, expr: Assign) -> Any:
        self.resolve_expression(expr.value)
        self.__resolve_expression_local(expr, expr.name)

    def __resolve_function(self, statement: FunctionStatement, kind: FunctionKind):
        """
        Resolve a function
        """

        enclosing_function = self.__current_function
        self.__current_function = kind

        self.__begin_scope()

        for parameter in statement.parameters:
            self.__declare(parameter)
            self.__define(parameter)

        self.resolve_statements(statement.body)

        self.__end_scope()

        self.__current_function = enclosing_function

    def visit_function_statement(self, statement: FunctionStatement) -> Any:
        self.__declare(statement.name)
        self.__define(statement.name)
        self.__resolve_function(statement, FunctionKind.FUNCTION)

    def visit_expression_statement(self, expr: ExpressionStatement) -> Any:
        self.resolve_expression(expr.expression)

    def visit_if_statement(self, statement: IfStatement) -> Any:
        self.resolve_expression(statement.condition)
        self.resolve_statement(statement.then_branch)

        if statement.else_branch is not None:
            self.resolve_statement(statement.else_branch)

    def visit_print_statement(self, statement: PrintStatement) -> Any:
        self.resolve_expression(statement.expression)

    def visit_return_statement(self, statement: ReturnStatement) -> Any:
        if self.__current_function != FunctionKind.FUNCTION:
            Error.error_token(statement.keyword, "Can't return from a top-level code")

        if statement.value is not None:
            self.resolve_expression(statement.value)

    def visit_while_statement(self, statement: WhileStatement) -> Any:
        self.resolve_expression(statement.condition)
        self.resolve_statement(statement.body)

    def visit_binary_expr(self, expr: Binary) -> Any:
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visit_call_expr(self, expr: Call) -> Any:
        self.resolve_expression(expr.callee)

        for argument in expr.arguments:
            self.resolve_expression(argument)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        self.resolve_expression(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return None

    def visit_logical_expr(self, expr: Logical) -> Any:
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visit_unary_expr(self, expr: Unary) -> Any:
        self.resolve_expression(expr.right)
