"""parser module"""

from typing import List

from ..scanner.token import Token, TokenKind
from ..ast.expr import Binary, Unary, Literal, Grouping
from ..ast.expr import Expr, Statement, PrintStatement, ExpressionStatement, \
    VarStatement, Variable, Assign, BlockStatement, IfStatement, Logical, \
    WhileStatement, Call, FunctionStatement, ReturnStatement
from ..error.error import ParserError, Error

class Parser:
    """
        Parse the tokens into a list of statement
    """

    def __init__(self, tokens: List[Token]):
        self.__current = 0
        self.__tokens = tokens

    def __expression(self) -> Expr:
        """
            Start parsing the grammar expressions from the top
        """
    
        return self.__assignment()

    def __is_at_end(self) -> bool:
        """
            Check if the curent cursor has reach the EOF token
        """
        
        return self.__peek().kind == TokenKind.EOF

    def __peek(self, index: int=None) -> Token:
        """
            get the current token
        """
        
        if index == None:
            index = self.__current
        
        return self.__tokens[index]
    
    def __peek_previous(self) -> Token:
        """
            Get the previous token
        """
        
        return self.__peek(self.__current - 1)
    
    def __check(self, kind: TokenKind) -> bool:
        """
            Compare the current token kind with a specific token kind
        """
        
        if self.__is_at_end():
            return False
        
        return self.__peek().kind == kind
    
    def __match(self, *kinds: TokenKind) -> bool:
        """
            Compare the current token kind with multiple token kinds
        """
        
        if ret := self.__peek().kind in kinds:
            self.__advance()

        return ret
    
    def __error(self, token: Token, message: str) -> ParserError:
        """
            Write a token error into stdout and return a `ParserError` instance
        """
        
        Error.error_token(token, message)

        return ParserError()
    
    def __consume(self, kind: TokenKind, message: str) -> Token:
        """
            Consume the current token only if it matches the token kind,
            otherwise, it becomes an error
        """
        
        if self.__check(kind):
            return self.__advance()
        
        raise self.__error(self.__peek(), message)
    
    def __advance(self) -> Token:
        """
            Move the cursor on the next token and return the previous one
        """
        
        if not self.__is_at_end():
            self.__current += 1
            
        return self.__peek_previous()
    
    def __or(self) -> Expr:
        """
            Or expression production
        """
        
        expr = self.__and()

        while self.__match(TokenKind.OR):
            operator = self.__peek_previous()
            right = self.__and()

            expr = Logical(expr, operator, right)
        
        return expr
    
    def __and(self) -> Expr:
        """
            And expression production
        """

        expr = self.__equality()
        
        while self.__match(TokenKind.AND):
            operator = self.__peek_previous()
            right = self.__equality()

            expr = Logical(expr, operator, right)
        
        return expr

    def __assignment(self):
        """
            Assignment expression production
        """
        
        expr = self.__or()
        
        if self.__match(TokenKind.EQUAL):
            equals = self.__peek_previous()
            value = self.__assignment()
        
            if type(expr) == Variable:
                return Assign(expr.name, value)
            
            self.__error(equals, "Invalid assignment target")
        
        return expr
    
    def __equality(self) -> Expr:
        """
            Equality expression production
        """

        expr = self.__comparison()
        
        while self.__match(
            TokenKind.BANG_EQUAL,
            TokenKind.EQUAL_EQUAL
        ):
            operator = self.__peek_previous()
            right = self.__comparison()
        
            expr = Binary(expr, operator, right)
        
        return expr

    def __comparison(self) -> Expr:
        """
            Comparison expression production
        """
        
        expr = self.__term()
        
        while self.__match(
            TokenKind.GREATER,
            TokenKind.GREATER_EQUAL,
            TokenKind.LESS,
            TokenKind.LESS_EQUAL
        ):
            operator = self.__peek_previous()
            right = self.__term()
            
            expr = Binary(expr, operator, right)
        
        return expr

    def __term(self) -> Expr:
        """
            Term expression production
        """
        
        expr = self.__factor()
        
        while self.__match(
            TokenKind.MINUS,
            TokenKind.PLUS
        ):
            operator = self.__peek_previous()
            right = self.__factor()
            
            expr = Binary(expr, operator, right)
        
        return expr
            
    def __factor(self) -> Expr:
        """
            Factor expression production
        """
        
        expr = self.__unary()
        
        while self.__match(
            TokenKind.SLASH,
            TokenKind.STAR
        ):
            operator = self.__peek_previous()
            right = self.__unary()
            
            expr = Binary(expr, operator, right)
        
        return expr
    
    def __finish_call(self, callee: Expr) -> Expr:
        """
            Generates a Call node
        """
        
        arguments = []
        
        while not self.__check(TokenKind.RIGHT_PAREN):
            arguments_size = len(arguments)
            
            if arguments_size >= 255:
                self.__error(self.__peek(), "Can't have more than 255 arguments")
            
            if arguments_size == 0:
                arguments.append(self.__expression())

            if self.__match(TokenKind.COMMA):
                arguments.append(self.__expression())
        
        paren = self.__consume(
            TokenKind.RIGHT_PAREN,
            "Expect ')' after function arguments"
        )

        return Call(callee, paren, arguments)
    
    def __call(self) -> Expr:
        """
            Call expression production
        """
        
        expr = self.__primary()
        
        while True:
            if not self.__match(TokenKind.LEFT_PAREN):
                break
            
            expr = self.__finish_call(expr)
        
        return expr
    
    def __unary(self) -> Expr:
        """
            Unary expression production
        """
        
        if self.__match(
            TokenKind.BANG,
            TokenKind.MINUS
        ):
            operator = self.__peek_previous()
            right = self.__unary()
            
            return Unary(operator, right)
        
        return self.__call()
    
    def __primary(self) -> Expr:
        """
            Parse a primary that is the last grammar production
        """
        
        if self.__match(TokenKind.FALSE):
            return Literal(False)
        
        if self.__match(TokenKind.TRUE):
            return Literal(True)
        
        if self.__match(TokenKind.NIL):
            return Literal(None)
        
        if self.__match(TokenKind.NUMBER, TokenKind.STRING):
            return Literal(self.__peek_previous().literal)
        
        if self.__match(TokenKind.LEFT_PAREN):
            expr = self.__expression()
            
            self.__consume(TokenKind.RIGHT_PAREN, "Expect ')'")
            
            return Grouping(expr)

        if self.__match(TokenKind.IDENTIFIER):
            return Variable(self.__peek_previous())
        
        raise self.__error(self.__peek(), "Expect expression")

    def __synchronize(self):
        """
            Synchronize the parser current cursor
        """
        
        self.__advance()
        
        while not self.__is_at_end():
            if self.__peek_previous().kind == TokenKind.SEMICOLON:
                return
            
            match self.__peek().kind:
                case TokenKind.CLASS: pass
                case TokenKind.FUN: pass
                case TokenKind.VAR: pass
                case TokenKind.FOR: pass
                case TokenKind.IF: pass
                case TokenKind.WHILE: pass
                case TokenKind.PRINT: pass
                case TokenKind.RETURN:
                    return
            
            self.__advance()
    
    def __print_statement(self) -> Statement:
        """
            Print statement production
        """
        
        value = self.__expression()
        
        self.__consume(TokenKind.SEMICOLON, "Expect ';' after value.")
        
        return PrintStatement(value)
    
    def __expression_statement(self) -> Statement:
        """
            Expression statement production
        """
        
        expr = self.__expression()
        
        self.__consume(TokenKind.SEMICOLON, "Expect ';' after expr.")
        
        return ExpressionStatement(expr)
    
    def __block_statement(self) -> List[Statement]:
        """
            Block statement production
        """
        
        statements = []
        
        while not self.__check(TokenKind.RIGHT_BRACE) and not self.__is_at_end():
            statements.append(self.__declaration())

        self.__consume(TokenKind.RIGHT_BRACE, "Expect '}' after block ")
        
        return statements
    
    def __if_statement(self) -> Statement:
        """
            If statement production
        """
        
        self.__consume(TokenKind.LEFT_PAREN, "Expect '(' before if condition")
        
        condition = self.__expression()
        
        self.__consume(TokenKind.RIGHT_PAREN, "Expect ')' before after condition")

        then_branch = self.__statement()
        else_branch = None
        
        if self.__match(TokenKind.ELSE):
            self.__advance()
            
            else_branch = self.__statement()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def __while_statement(self) -> Statement:
        """
            While statement production
        """
        
        self.__consume(TokenKind.LEFT_PAREN, "Expect '(' after while")
        
        condition = self.__expression()
        
        self.__consume(TokenKind.RIGHT_PAREN, "Expect ')' after condition")
    
        body = self.__statement()
        
        return WhileStatement(condition, body)
    
    def __for_statement(self) -> Statement:
        """
            For statement production
        """
        
        self.__consume(TokenKind.LEFT_PAREN, "Expect '(' after for")
        
        # Initializer
        if self.__match(TokenKind.VAR):
            initializer = self.__var_declaration()
        elif self.__match(TokenKind.SEMICOLON):
            initializer = None
        else:
            initializer = self.__expression_statement()
        
        # Condition
        condition = None
        if not self.__check(TokenKind.SEMICOLON):
            condition = self.__expression()
        
        self.__consume(TokenKind.SEMICOLON, "Expect ';' after condition")

        # Increment    
        increment = None
        if not self.__check(TokenKind.RIGHT_PAREN):
            increment = self.__expression()
        
        self.__consume(TokenKind.RIGHT_PAREN, "Expect ')' after for")
        
        body = self.__statement()
        
        if increment != None:
            body = BlockStatement(
                [
                    body, ExpressionStatement(increment)
                ]
            )
        
        if condition == None:
            condition = Literal(True)
        
        body = WhileStatement(condition, body)
        
        if initializer != None:
            body = BlockStatement(
                [
                    ExpressionStatement(initializer), body
                ]
            )
        
        return body
        
    def __return_statement(self) -> Statement:
        """
            Return statement production
        """

        keyword = self.__peek_previous()
        value = None
        
        if not self.__check(TokenKind.SEMICOLON):
            value = self.__expression()
        
        self.__consume(TokenKind.SEMICOLON, "Expect ';' after return value")

        return ReturnStatement(keyword, value)
    
    def __statement(self) -> Statement:
        """
            Statement production
        """

        if self.__match(TokenKind.PRINT):
            return self.__print_statement()
        
        if self.__match(TokenKind.LEFT_BRACE):
            return BlockStatement(self.__block_statement())
        
        if self.__match(TokenKind.IF):
            return self.__if_statement()
    
        if self.__match(TokenKind.WHILE):
            return self.__while_statement()
        
        if self.__match(TokenKind.FOR):
            return self.__for_statement()
        
        if self.__match(TokenKind.RETURN):
            return self.__return_statement()
    
        return self.__expression_statement()
    
    def __var_declaration(self) -> Statement:
        """
            Var statement production
        """
        
        name = self.__consume(TokenKind.IDENTIFIER, "Expect variable name")
    
        initializer = None
        if self.__match(TokenKind.EQUAL):
            initializer = self.__expression()
        
        self.__consume(TokenKind.SEMICOLON, "Expect ';' after variable declaration")

        return VarStatement(name, initializer)
    
    def __function(self, kind: str) -> Statement:
        name = self.__consume(TokenKind.IDENTIFIER, f"Expect {kind} name")
    
        self.__consume(TokenKind.LEFT_PAREN, f"Expect '(' after {kind} name")
    
        parameters = []
        
        if not self.__check(TokenKind.RIGHT_PAREN):
            parameters.append(
                self.__consume(TokenKind.IDENTIFIER, "Expect parameter name")
            )
            
            while self.__match(TokenKind.COMMA):
                if len(parameters) >= 255:
                    self.__error(self.__peek(), "Parameters amount cannot exceed 255")

                parameters.append(
                    self.__consume(TokenKind.IDENTIFIER, "Expect parameter name")
                )
            
        self.__consume(TokenKind.RIGHT_PAREN, f"Expect ')' after {kind} parameters")
        self.__consume(TokenKind.LEFT_BRACE, "Expect '{' before " + kind + "body")
        
        body = self.__block_statement()
        
        return FunctionStatement(name, parameters, body)        
        
    def __declaration(self) -> Statement:
        """
            Top grammar production
        """
        
        try:
            if self.__match(TokenKind.VAR):
                return self.__var_declaration()
            
            if self.__match(TokenKind.FUN):
                return self.__function("function")
    
            return self.__statement()
        except ParserError:
            self.__synchronize()
            
        return None

    def parse(self) -> List[Statement] | None:
        """
            Parse the tokens, then return a list of statements,
            if there is an error during parsing, None is returned
        """
        
        statements = []

        try:
            while not self.__is_at_end():
                statements.append(self.__declaration())
        except ParserError:
            return None

        return statements
