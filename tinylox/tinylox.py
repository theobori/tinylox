from sys import argv

from .lox import Lox


def main():
    av = argv[1:]
    ac = len(av)

    if ac != 1:
        exit(1)

    Lox.interpret_from_file(av[0])
