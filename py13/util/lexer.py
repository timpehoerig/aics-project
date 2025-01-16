import re
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class TokenDesc[T]:
    regex: re.Pattern[str]
    build: Callable[[str], Optional[T]]


@dataclass(frozen=True)
class LexerError(Exception):
    pos: int

    def __str__(self) -> str:
        return f"Lexer error at position {self.pos}."


type Lexer[T] = list[TokenDesc[T]]


def lex[T](lexer: Lexer[T], s: str) -> list[T]:
    i = 0
    toks: list[T] = []
    while i < len(s):
        longest_match = None
        for td in lexer:
            m = td.regex.match(s, i)
            if m is None:
                continue
            end = m.end()
            matched_text = m.group()
            if longest_match is None or longest_match[0] < end:
                longest_match = (end, matched_text, td)
        if longest_match is None:
            raise LexerError(i)
        (end, matched_text, td) = longest_match
        tok = td.build(matched_text)
        if tok is not None:
            toks.append(tok)
        i = end
    return toks
