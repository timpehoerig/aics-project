import util.parser as parser
from util.parser import Grammar, TokenMatcher, Rule
from util.immutable_list import ilist

from py13_pyttr_AST import *

from lexer import (
    Token,
    TId,
    TColon,
    TQuestion,
    TParenL,
    TParenR,
    TEquals,
    TNewLine,
    TType,
    TBType,
    TArrowL,
    TFunc,
)

t_ident:    TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TId,        "identifier")
t_colon:    TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TColon,     ":")
t_question: TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TQuestion,  "?")
t_parenL:   TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TParenL,    "(")
t_parenR:   TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TParenR,    ")")
t_equal:    TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TEquals,    "=")
t_arrowL:   TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TArrowL,    "<-")
t_newline:  TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TNewLine,   "newline")
t_type:     TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TType,      "Type")
t_btype:    TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TBType,     "BType")
t_func:     TokenMatcher[Token] = TokenMatcher(lambda t: type(t) is TFunc,      "function")

# <prog>  -> <newl*> <stmt*> <newl*>
# <newl*> -> newline <newl*> |
# <stmt*> -> <stmt> newline <newl*> <stmt*> |
# <stmt>  -> <any :> <id> | = <any ?> <id> | Type <id> | BType <id> | <id> <- <func>
# <id>    -> ...
# <any :> -> ...
# <any ?> -> ...


pyttr_grammar: Grammar[Token] = [
    Rule("newl*",   ilist(t_newline, "newl*"),                  lambda _1, _2: ilist()),
    Rule("newl*",   ilist(),                                    lambda: ilist()),

    Rule("prog",    ilist("newl*", "stmt*", "newl*"),           lambda _1, i, _2: i),

    Rule("stmt*",   ilist("stmt", t_newline, "newl*", "stmt*"), lambda s, _1, _2, ss: ilist(s) + ss),
    Rule("stmt*",   ilist(),                                    lambda: ilist()),

    Rule("stmt",    ilist(t_colon, t_ident),                    lambda any, type: SJudgement(any.val[:-2], type.val)),
    Rule("stmt",    ilist(t_question, t_ident),                 lambda any, type: SQuery(any.val[:-2], type.val)),
    Rule("stmt",    ilist(t_parenL, "stmt", t_parenR),          lambda _1, s, _2: s),
    Rule("stmt",    ilist(t_type, t_ident),                     lambda _, ident: SType(ident.val)),
    Rule("stmt",    ilist(t_btype, t_ident),                    lambda _, ident: SBType(ident.val)),
    Rule("stmt",    ilist(t_ident, t_arrowL, t_func),           lambda i, _, f: SLearnWitnessCond(i.val, f.val)),
]


def parse(toks: list[Token], verbose: bool) -> Program:
    try:
        return parser.parse_unique(pyttr_grammar, "prog", toks, verbose)
    except parser.UnexpectedToken as err:
        raise Exception(f"Expected {err.expected} at position {err.token_index}")
    except parser.AmbiguousParse as err:
        raise Exception("Ambigious Parse", err)
