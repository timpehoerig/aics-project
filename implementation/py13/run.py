from lexer import lex
from parser import parse
from interpreter import interprete
import argparse


def read(path: str = "./test.txt") -> str:
    with open(path, "r") as file:
        return file.read()


par = argparse.ArgumentParser()
par.add_argument("filename")


if __name__ == "__main__":
    args = par.parse_args()
    src = read(args.filename)
    tokens = lex(src)
    program = parse(tokens, False)
    print(program)
    interprete(program)
