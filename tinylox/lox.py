"""lox module"""

from .scanner.scanner import Scanner
from .ast.parser import Parser
from .ast.interpreter import Interpreter
from .error.error import Error

PROMPT_PREFIX = "> "


class Lox:
    """
    Lox interpreter entry point
    """

    def __interpret(source: str):
        """
        Interpret from a source string
        """

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()

        if Error.had_error:
            return

        interpreter = Interpreter()
        interpreter.interpret(statements)

        if Error.had_runtime_error:
            return

    def interpret_from_file(path: str):
        """
        Interpret from a file
        """

        with open(path) as f:
            data = f.read()

        Lox.__interpret(data)

        if Error.had_error:
            exit(1)
