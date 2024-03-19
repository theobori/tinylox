"""error module"""

from ..scanner.token import Token, TokenKind

class ParserError(Exception):
    """
        Exception for the parser
    """
    
    pass

class RuntimeErrorL(Exception):
    """
        Exception for the runtime (interpreter)
    """

    def __init__(self, token: Token, *args: object):
        super().__init__(*args)

        self.__token = token

    @property
    def token(self) -> Token:
        """
            Get the token
        """

        return self.__token

class Error:
    """
        It manages the Lox workflow
    """

    had_error = False
    had_runtime_error = False

    def error_reset():
        """
            Reset the error flags
        """

        Error.had_error = False
        Error.had_runtime_error = False
    
    def __report(line: int, where: str, message: str):
        """
            Write an error/indication on stdout for the user
        """ 
        
        print("[line", str(line) + "] Error", where, ":", message)
        
        Error.had_error = True

    def error(line: int, message: str):
        """
            Report an error
        """

        Error.__report(line, "", message)

    def error_token(token: Token, message: str):
        """
            Report an error based on a token
        """
        
        if token.kind == TokenKind.EOF:
            where = " at end"
        else:
            where = " at '" + token.lexeme + "'"
        
        Error.__report(token.line, where, message)
