"""main module"""

from sys import argv

from interpreter.lox import Lox

def main():
    av = argv[1:]
    ac = len(av)
    
    if ac < 1:
        Lox.interpret_repl()
    elif ac == 1:
        Lox.interpret_from_file(av[0])
    else:
        exit(1)

if __name__ == "__main__":
    main()
