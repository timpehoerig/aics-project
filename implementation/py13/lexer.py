from dataclasses import dataclass
import re

import util.lexer as lexer
from util.lexer import TokenDesc

# Token data types

type Token = TId | TColon | TQuestion | TParenL | TParenR | TEquals | TNewLine | TType | TBType | TArrowL | TFunc


@dataclass(frozen=True)
class TId:
    val: str


@dataclass(frozen=True)
class TColon:
    val: str


@dataclass(frozen=True)
class TQuestion:
    val: str


@dataclass(frozen=True)
class TParenL:
    pass


@dataclass(frozen=True)
class TParenR:
    pass


@dataclass(frozen=True)
class TEquals:
    pass


@dataclass(frozen=True)
class TNewLine:
    pass


@dataclass(frozen=True)
class TType:
    pass


@dataclass(frozen=True)
class TBType:
    pass


@dataclass(frozen=True)
class TArrowL:
    pass


@dataclass(frozen=True)
class TFunc:
    val: str


# Lexer

lvar_lexer: lexer.Lexer[Token] = [
    TokenDesc(re.compile("Type"),                 lambda _: TType()),
    TokenDesc(re.compile("BType"),                lambda _: TBType()),
    TokenDesc(re.compile("lambda .*"),            lambda s: TFunc(s)),
    TokenDesc(re.compile("[a-zA-Z][a-zA-Z0-9]*"), lambda s: TId(s)),
    TokenDesc(re.compile("\\("),                  lambda _: TParenL()),
    TokenDesc(re.compile("\\)"),                  lambda _: TParenR()),
    TokenDesc(re.compile(".+ :"),                 lambda s: TColon(s)),
    TokenDesc(re.compile(".+ \\?"),               lambda s: TQuestion(s)),
    TokenDesc(re.compile("="),                    lambda _: TEquals()),
    TokenDesc(re.compile("<-"),                   lambda _: TArrowL()),
    TokenDesc(re.compile("\n"),                   lambda _: TNewLine()),
    TokenDesc(re.compile("[ \t]+"),               lambda _: None),
    TokenDesc(re.compile("#[^\n]*"),              lambda _: None),
]


def lex(src: str) -> list[Token]:
    try:
        return lexer.lex(lvar_lexer, src)
    except lexer.LexerError as err:
        raise Exception(err)
