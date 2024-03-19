"""ast module"""

from typing import List
from io import TextIOWrapper
from sys import argv

IMPORTS = """from ..scanner.token import Token
from typing import Any, List
from dataclasses import dataclass
"""

EXPR_CLASS_NAME = "Expr"

CLASS_TEMPLATE = """class %s:
    def accept(self, _: Visitor) -> Any:
        \"\"\"
            Call a method from a visitor,
            the method should be made for the expression or the statement
        \"\"\"

        raise Exception(\"Not implemented\")
"""

TYPES = (
    ("Binary", f"{EXPR_CLASS_NAME} left, Token operator, {EXPR_CLASS_NAME} right"),
    ("Logical", f"{EXPR_CLASS_NAME} left, Token operator, {EXPR_CLASS_NAME} right"),
    ("Grouping", f"{EXPR_CLASS_NAME} expression"),
    ("Literal", "Any value"),
    ("Assign", "Token name, Expr value"),
    ("Unary", f"Token operator, {EXPR_CLASS_NAME} right"),
    ("Variable", "Token name"),
    ("Call", f"{EXPR_CLASS_NAME} callee, Token paren, List[{EXPR_CLASS_NAME}] arguments")
)

STATEMENT_CLASS_NAME = "Statement"

STATEMENTS = (
    ("Expression", f"{EXPR_CLASS_NAME} expression"),
    ("Print", f"{EXPR_CLASS_NAME} expression"),
    ("Return", f"Token keyword, {EXPR_CLASS_NAME} value"),
    ("Var", f"Token name, {EXPR_CLASS_NAME} initializer"),
    ("Block", f"List[{STATEMENT_CLASS_NAME}] statements"),
    ("If", f"{EXPR_CLASS_NAME} condition, {STATEMENT_CLASS_NAME} then_branch, {STATEMENT_CLASS_NAME} else_branch"),
    ("While", f"{EXPR_CLASS_NAME} condition, {STATEMENT_CLASS_NAME} body"),
    ("Function", f"Token name, List[Token] parameters, List[{STATEMENT_CLASS_NAME}] body")
)

def writeln(f: TextIOWrapper, s: str="") -> int:
    return f.write(s + "\n")

def write_visitor_interface(f: TextIOWrapper):
    writeln(f, "class Visitor:")
    
    for name, _ in TYPES:
        writeln(f, "    def visit_" + name.lower() + "_expr(self, expr: " + name + ") -> Any:")
        writeln(f, "        \"\"\"")
        writeln(f, "            Operates on a " + name + " expression")
        writeln(f, "        \"\"\"")
        writeln(f)
        writeln(f, "        raise Exception(\"Not implemented\")")
        writeln(f)
    
    for name, _ in STATEMENTS:
        writeln(f, "    def visit_" + name.lower() + "_statement(self, statement: " + name + STATEMENT_CLASS_NAME + ") -> Any:")
        writeln(f, "        \"\"\"")
        writeln(f, "            Operates on a " + name + " statement")
        writeln(f, "        \"\"\"")
        writeln(f)
        writeln(f, "        raise Exception(\"Not implemented\")")
        writeln(f)

def write_dataclass(f: TextIOWrapper, base: str, name: str, members: str):
    writeln(f, "@dataclass")
    writeln(f, "class " + name + "(" + base + "):")
    
    writeln(f, "    \"\"\"")
    writeln(f, "        " + name + " " + base)
    writeln(f, "    \"\"\"")
    writeln(f)
    
    members = members.split(",")

    for member in members:
        member = member.strip()
        _type, param = member.split(" ")

        writeln(f, "    " + param + ": " + _type)
    
    name = name.replace(base, "")
    
    writeln(f)
    writeln(f, "    def accept(self, visitor: Visitor) -> Any:")
    writeln(f, "        return visitor.visit_" + name.lower() + "_" + base.lower() + "(self)")

if __name__ == "__main__":
    av = argv[1:]
    ac = len(av)
    
    if ac < 1:
        exit(1)
    
    path = av.pop(0)
    
    with open(path, "w+") as f:
        writeln(f, IMPORTS)
        
        writeln(f, "class Visitor: pass")
        writeln(f)
        
        writeln(f, CLASS_TEMPLATE % EXPR_CLASS_NAME)

        for name, members in TYPES:
            write_dataclass(f, EXPR_CLASS_NAME, name, members)
            writeln(f)

        writeln(f, CLASS_TEMPLATE % STATEMENT_CLASS_NAME)
        writeln(f)

        for name, members in STATEMENTS:
            write_dataclass(f, STATEMENT_CLASS_NAME, name + STATEMENT_CLASS_NAME, members)
            writeln(f)

        writeln(f)
        
        write_visitor_interface(f)
