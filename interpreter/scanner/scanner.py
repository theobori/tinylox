"""scanner module"""

from typing import List, Any

from .token import TokenKind, Token
from ..error.error import Error

RESERVED_WORDS = {
    "and": TokenKind.AND,
    "class": TokenKind.CLASS,
    "else": TokenKind.ELSE,
    "false": TokenKind.FALSE,
    "for": TokenKind.FOR,
    "fun": TokenKind.FUN,
    "if": TokenKind.IF,
    "nil": TokenKind.NIL,
    "or": TokenKind.OR,
    "print": TokenKind.PRINT,
    "return": TokenKind.RETURN,
    "super": TokenKind.SUPER,
    "this": TokenKind.THIS,
    "true": TokenKind.TRUE,
    "var": TokenKind.VAR,
    "while": TokenKind.WHILE
}

def is_alphanum(char: str) -> bool:
    """
        Check if a string is an identifier,
        in our case it is used to check is a byte is part of
        an identifier
    """
    
    return char.isalnum() or char == "_"

class Scanner:
    """
        Lox lexer, it generates the tokens from the source code
    """

    def __init__(self, source: str):
        self.__source = source
        
        self.__tokens = []
        self.__start = 0
        self.__current = 0
        self.__line = 1
    
    def set_source(self, value: str):
        """
            Set the raw source code as Python string
        """
        
        self.__source = value

    @property
    def tokens(self) -> List[Token]:
        """
            Get the tokens list
        """

        return self.__tokens

    def __peek(self, index: int=None) -> str:
        """
            Get the current character
        """

        if self.__is_at_end():
            return "\0"
        
        if not index:
            index = self.__current

        return self.__source[index]

    def __peek_next(self) -> str:
        """
            Get the next character
        """

        return self.__peek(self.__current + 1)
    
    def __advance(self) -> str:
        """
            Move the current cursor to the next character
            and return the previous one
        """

        char = self.__peek()
    
        self.__current += 1
    
        return char

    def __add_token(self, kind: TokenKind, literal: Any=None):
        """
            Add a token to the token list in function of the
            start and current cursors position
        """

        lexeme = self.__source[self.__start:self.__current]
        token = Token(kind, lexeme, literal, self.__line)
        
        self.__tokens.append(token)

    def __match(self, char: str) -> bool:
        """
            Check if a character match the current one
        """
        
        if self.__is_at_end():
            return False
        
        if self.__peek() != char:
            return False
        
        self.__current += 1

        return True

    def __string(self):
        """
            Add a string token
        """
        
        while (char := self.__peek()) != "\"":
            if self.__is_at_end():
                Error.error(self.__line, "Unterminated string")
                return

            if char == "\n":
                self.__line += 1

            self.__advance()
        
        self.__advance()
        
        literal = self.__source[self.__start + 1:self.__current - 1]
        
        self.__add_token(TokenKind.STRING, literal)
        
    def __number(self):
        """
            Add a number token
        """
        
        dot = False

        while (char := self.__peek()).isdigit() or char == ".":
            if char == "." :
                if dot == True or not self.__peek_next().isdigit():
                    Error.error(self.__line, "Invalid number")
                    return
    
                dot = True

            self.__advance()
        
        literal = self.__source[self.__start:self.__current]
        literal = float(literal)
        
        self.__add_token(TokenKind.NUMBER, literal)
        
    def __identifier(self):
        """
            Add an identifier token
        """

        while is_alphanum(self.__peek()):
            self.__advance()
        
        keyword = self.__source[self.__start:self.__current]
        token_kind = RESERVED_WORDS.get(keyword)

        if not token_kind:
            token_kind = TokenKind.IDENTIFIER

        self.__add_token(token_kind)
        
    def __slash(self):
        """
            Manages the comments and add a slash token if possible
        """
        
        if self.__match("/"):
            while self.__peek() != "\n" and not self.__is_at_end():
                self.__advance()
            
            return
            
        if self.__match("*"):
            while self.__peek() != "*" or self.__peek_next() != "/":
                if self.__peek() == "\n":
                    self.__line += 1

                if self.__is_at_end():
                    Error.error(self.__line, "Unterminated comment block")
                    return

                self.__advance()
            
            self.__advance()
            self.__advance()

            return

        self.__add_token(TokenKind.SLASH)
                
    def __scan_token(self):
        """
            Scan the current character and add it as a token
        """
        
        char = self.__advance()
        
        match char:
            case "(": self.__add_token(TokenKind.LEFT_PAREN)
            case ")": self.__add_token(TokenKind.RIGHT_PAREN)
            case "{": self.__add_token(TokenKind.LEFT_BRACE)
            case "}": self.__add_token(TokenKind.RIGHT_BRACE)
            case ",": self.__add_token(TokenKind.COMMA)
            case ".": self.__add_token(TokenKind.DOT)
            case "-": self.__add_token(TokenKind.MINUS)
            case "+": self.__add_token(TokenKind.PLUS)
            case ";": self.__add_token(TokenKind.SEMICOLON)
            case "*": self.__add_token(TokenKind.STAR)
            case "!": self.__add_token(TokenKind.BANG_EQUAL if self.__match("=") else TokenKind.BANG)
            case "=": self.__add_token(TokenKind.EQUAL_EQUAL if self.__match("=") else TokenKind.EQUAL)
            case "<": self.__add_token(TokenKind.LESS_EQUAL if self.__match("=") else TokenKind.LESS)
            case ">": self.__add_token(TokenKind.GREATER_EQUAL if self.__match("=") else TokenKind.GREATER)
            case "\r" | "\t" | " ": pass
            case "\n":
                self.__line += 1
            case "/":
                self.__slash()                    
            case "\"":
                self.__string()
            case _:
                if char.isdigit():
                    self.__number()
                elif char.isalpha():
                    self.__identifier()
                else:    
                    Error.error(self.__line, "Unexpected error")
        
    def __is_at_end(self) -> bool:
        """
            Check if the curent cursor has reach the end of the source code
        """
        
        return self.__current >= len(self.__source)
    
    def scan_tokens(self) -> List[Token]:
        """
            Transform the source code from string into tokens,
            and then return them
        """
        
        while self.__is_at_end() == False:
            self.__start = self.__current
            
            self.__scan_token()
            
        eof_token = Token(TokenKind.EOF, "", "", self.__line)
        
        self.__tokens.append(eof_token)
        
        return self.__tokens
