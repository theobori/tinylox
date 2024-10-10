from ..scanner.token import Token
from typing import Any, List
from dataclasses import dataclass


class Visitor:
    pass


class Expr:
    def accept(self, _: Visitor) -> Any:
        """
        Call a method from a visitor,
        the method should be made for the expression or the statement
        """

        raise Exception("Not implemented")


@dataclass
class Binary(Expr):
    """
    Binary Expr
    """

    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_binary_expr(self)


@dataclass
class Logical(Expr):
    """
    Logical Expr
    """

    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_logical_expr(self)


@dataclass
class Grouping(Expr):
    """
    Grouping Expr
    """

    expression: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    """
    Literal Expr
    """

    value: Any

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_literal_expr(self)


@dataclass
class Assign(Expr):
    """
    Assign Expr
    """

    name: Token
    value: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_assign_expr(self)


@dataclass
class Unary(Expr):
    """
    Unary Expr
    """

    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary_expr(self)


@dataclass
class Variable(Expr):
    """
    Variable Expr
    """

    name: Token

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_variable_expr(self)


@dataclass
class Call(Expr):
    """
    Call Expr
    """

    callee: Expr
    paren: Token
    arguments: List[Expr]

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_call_expr(self)


class Statement:
    def accept(self, _: Visitor) -> Any:
        """
        Call a method from a visitor,
        the method should be made for the expression or the statement
        """

        raise Exception("Not implemented")


@dataclass
class ExpressionStatement(Statement):
    """
    ExpressionStatement Statement
    """

    expression: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_expression_statement(self)


@dataclass
class PrintStatement(Statement):
    """
    PrintStatement Statement
    """

    expression: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_print_statement(self)


@dataclass
class ReturnStatement(Statement):
    """
    ReturnStatement Statement
    """

    keyword: Token
    value: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_return_statement(self)


@dataclass
class VarStatement(Statement):
    """
    VarStatement Statement
    """

    name: Token
    initializer: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_var_statement(self)


@dataclass
class BlockStatement(Statement):
    """
    BlockStatement Statement
    """

    statements: List[Statement]

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_block_statement(self)


@dataclass
class IfStatement(Statement):
    """
    IfStatement Statement
    """

    condition: Expr
    then_branch: Statement
    else_branch: Statement

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    """
    WhileStatement Statement
    """

    condition: Expr
    body: Statement

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_while_statement(self)


@dataclass
class FunctionStatement(Statement):
    """
    FunctionStatement Statement
    """

    name: Token
    parameters: List[Token]
    body: List[Statement]

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_function_statement(self)


class Visitor:
    def visit_binary_expr(self, expr: Binary) -> Any:
        """
        Operates on a Binary expression
        """

        raise Exception("Not implemented")

    def visit_logical_expr(self, expr: Logical) -> Any:
        """
        Operates on a Logical expression
        """

        raise Exception("Not implemented")

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        """
        Operates on a Grouping expression
        """

        raise Exception("Not implemented")

    def visit_literal_expr(self, expr: Literal) -> Any:
        """
        Operates on a Literal expression
        """

        raise Exception("Not implemented")

    def visit_assign_expr(self, expr: Assign) -> Any:
        """
        Operates on a Assign expression
        """

        raise Exception("Not implemented")

    def visit_unary_expr(self, expr: Unary) -> Any:
        """
        Operates on a Unary expression
        """

        raise Exception("Not implemented")

    def visit_variable_expr(self, expr: Variable) -> Any:
        """
        Operates on a Variable expression
        """

        raise Exception("Not implemented")

    def visit_call_expr(self, expr: Call) -> Any:
        """
        Operates on a Call expression
        """

        raise Exception("Not implemented")

    def visit_expression_statement(self, statement: ExpressionStatement) -> Any:
        """
        Operates on a Expression statement
        """

        raise Exception("Not implemented")

    def visit_print_statement(self, statement: PrintStatement) -> Any:
        """
        Operates on a Print statement
        """

        raise Exception("Not implemented")

    def visit_return_statement(self, statement: ReturnStatement) -> Any:
        """
        Operates on a Return statement
        """

        raise Exception("Not implemented")

    def visit_var_statement(self, statement: VarStatement) -> Any:
        """
        Operates on a Var statement
        """

        raise Exception("Not implemented")

    def visit_block_statement(self, statement: BlockStatement) -> Any:
        """
        Operates on a Block statement
        """

        raise Exception("Not implemented")

    def visit_if_statement(self, statement: IfStatement) -> Any:
        """
        Operates on a If statement
        """

        raise Exception("Not implemented")

    def visit_while_statement(self, statement: WhileStatement) -> Any:
        """
        Operates on a While statement
        """

        raise Exception("Not implemented")

    def visit_function_statement(self, statement: FunctionStatement) -> Any:
        """
        Operates on a Function statement
        """

        raise Exception("Not implemented")
