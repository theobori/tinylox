"""interpreter module"""

from typing import Any, List
from sys import stderr

from ..error.error import RuntimeErrorL, Error
from ..scanner.token import TokenKind, Token
from .expr import (
    ExpressionStatement,
    PrintStatement,
    Visitor,
    Binary,
    Grouping,
    Literal,
    Unary,
    Expr,
    Statement,
    VarStatement,
    Variable,
    Assign,
    BlockStatement,
    IfStatement,
    Logical,
    WhileStatement,
    Call,
    FunctionStatement,
    ReturnStatement,
)
from .environment import Environment
from .callable import LoxCallable
from .function import LoxFunction
from .clock import Clock
from ._return import Return


class Interpreter(Visitor):
    """
    AST interpreter
    """

    def __init__(self):
        self.globals = Environment()
        self.__environment = self.globals

        self.globals.define("clock", Clock)

    def __evaluate(self, expr: Expr) -> Any:
        """
        Evaluate an expression node
        """

        return expr.accept(self)

    def __check_number_operand(self, operator: Token, operand: Any):
        """
        Check if a value is a float
        """

        if type(operand) == float:
            return

        raise RuntimeErrorL(operator, "Operand must be a number")

    def __check_number_operands(self, operator: Token, left: Any, right: Any):
        """
        Check if an operation includes two floats
        """

        self.__check_number_operand(operator, left)
        self.__check_number_operand(operator, right)

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = self.__evaluate(expr.left)
        right = self.__evaluate(expr.right)

        match expr.operator.kind:
            case TokenKind.MINUS:
                self.__check_number_operands(expr.operator, left, right)
                return left - right
            case TokenKind.STAR:
                self.__check_number_operands(expr.operator, left, right)
                return left * right
            case TokenKind.SLASH:
                self.__check_number_operands(expr.operator, left, right)
                return left / right
            case TokenKind.PLUS:
                match left, right:
                    case str(), str():
                        return left + right
                    case float(), float():
                        return left + right

                raise RuntimeErrorL(
                    expr.operator, "Operands must be two numbers or two strings"
                )
            case TokenKind.GREATER:
                self.__check_number_operands(expr.operator, left, right)
                return left > right
            case TokenKind.GREATER_EQUAL:
                self.__check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenKind.LESS:
                self.__check_number_operands(expr.operator, left, right)
                return left < right
            case TokenKind.LESS_EQUAL:
                self.__check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenKind.BANG_EQUAL:
                return left != right
            case TokenKind.EQUAL_EQUAL:
                return left == right

        return None

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.__environment.get(expr.name)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self.__evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def __is_truthy(self, obj: Any) -> bool:
        """
        Handle operation on a boolean `obj`
        """

        match obj:
            case bool():
                return obj
            case None:
                return False

        return True

    def visit_unary_expr(self, expr: Unary) -> Any:
        right = self.__evaluate(expr.right)

        match expr.operator.kind:
            case TokenKind.MINUS:
                self.__check_number_operand(expr.operator, right)

                return -float(right)
            case TokenKind.BANG:
                return self.__is_truthy(right)

        return None

    def visit_expression_statement(self, statement: ExpressionStatement) -> Any:
        self.__evaluate(statement.expression)

    def visit_print_statement(self, statement: PrintStatement) -> Any:
        value = self.__evaluate(statement.expression)
        value_str = self.__stringify(value)

        print(value_str)

    def visit_var_statement(self, statement: VarStatement) -> Any:
        value = None

        if statement.initializer is not None:
            value = self.__evaluate(statement.initializer)

        self.__environment.define(statement.name.lexeme, value)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self.__evaluate(expr.value)

        self.__environment.assign(expr.name, value)

        return value

    def visit_function_statement(self, statement: FunctionStatement) -> Any:
        f = LoxFunction(statement, self.__environment)

        self.__environment.define(statement.name.lexeme, f)

    def execute_block(self, statements: List[Statement], environment: Environment):
        """
        Evaluate a block
        """

        previous = self.__environment

        try:
            self.__environment = environment

            for statement in statements:
                self.__execute(statement)
        finally:
            self.__environment = previous

    def visit_block_statement(self, statement: BlockStatement) -> Any:
        self.execute_block(statement.statements, Environment(self.__environment))

    def visit_if_statement(self, statement: IfStatement) -> Any:
        if self.__is_truthy(self.__evaluate(statement.condition)):
            self.__execute(statement.then_branch)
        elif statement.else_branch:
            self.__execute(statement.else_branch)

    def visit_logical_expr(self, expr: Logical) -> Any:
        left = self.__evaluate(expr.left)

        if expr.operator.kind == TokenKind.OR:
            if self.__is_truthy(left):
                return left
        # AND case
        else:
            if not self.__is_truthy(left):
                return left

        return self.__evaluate(expr.right)

    def visit_while_statement(self, statement: WhileStatement) -> Any:
        while self.__is_truthy(self.__evaluate(statement.condition)):
            self.__execute(statement.body)

    def visit_call_expr(self, expr: Call) -> Any:
        callee = self.__evaluate(expr.callee)

        if not isinstance(callee, LoxCallable):
            raise RuntimeErrorL(expr.paren, "Can only call function and classes")

        callee: LoxCallable = callee

        arity = callee.arity()
        arguments_size = len(expr.arguments)

        if arguments_size != arity:
            raise RuntimeErrorL(
                expr.paren, f"Expected {arity} arguments but got {arguments_size}"
            )

        arguments = list(map(self.__evaluate, expr.arguments))

        return callee(self, arguments)

    def visit_return_statement(self, statement: ReturnStatement) -> Any:
        value = None

        if statement.value is not None:
            value = self.__evaluate(statement.value)

        raise Return(value)

    def __stringify(self, obj: Any) -> str:
        """
        Turns any value into a string
        """

        if obj is None:
            return "nil"

        return str(obj)

    def runtime_error(error: RuntimeErrorL):
        """
        Write into stdout a runtime error and
        turn on the runtime error flag
        """

        print(*error.args, "\n[line", str(error.token.line) + "]", file=stderr)

        Error.had_runtime_error = True

    def __execute(self, statement: Statement):
        """
        Evaluate a statement node
        """

        statement.accept(self)

    def interpret(self, statements: List[Statement]):
        """
        Interpret a list of statements (node)
        """

        try:
            for statement in statements:
                self.__execute(statement)
        except RuntimeErrorL as error:
            Interpreter.runtime_error(error)
