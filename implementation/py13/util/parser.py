from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence, TypeVar, Union

from util.immutable_list import IList, ilist

# Basic Earley Implementation #################################################
T = TypeVar("T", covariant=True)


@dataclass(frozen=True)
class Phantom[T]:
    pass


@dataclass(frozen=True)
class TokenMatcher(Phantom[T]):
    pred: Callable[[T], bool]
    err: str


# A non-terminal symbol (`str`) or terminal symbol (`TokenMatcher`)
type Sym[T] = str | TokenMatcher[T]


# Hack to make type inference in strict-mode happy...
# In non-strict-mode, we could also just use `Any` instead of `AnyCallable`.
type AnyCallable = Union[
    Callable[[], Any],
    Callable[[Any], Any],
    Callable[[Any, Any], Any],
    Callable[[Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any], Any],
    Callable[[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any], Any],
]


@dataclass(frozen=True)
class Rule(Phantom[T]):
    lhs: str
    rhs: IList[Sym[T]]
    action: AnyCallable = field(compare=False, hash=False)


@dataclass(frozen=True)
class DottedRule(Phantom[T]):
    rule: Rule[T]
    dot: int
    start: int
    values: IList[Any]

    def done(self) -> bool:
        return self.dot == len(self.rule.rhs)

    def dotted_sym(self) -> Optional[Sym[T]]:
        if self.dot == len(self.rule.rhs):
            return None
        else:
            return self.rule.rhs[self.dot]


type Grammar[T] = list[Rule[T]]
type Chart[T] = list[set[DottedRule[T]]]


def chart_to_str[T](chart: Chart[T]) -> str:
    s = ""
    for i, c in enumerate(chart):
        s += f"{i}:\n"
        for dr in c:
            s += "  " + dr.rule.lhs + " →"
            for i, sym in enumerate(dr.rule.rhs):
                if i == dr.dot:
                    s += " ."
                match sym:
                    case str(x):
                        s += f" {x}"
                    case TokenMatcher(_, n):
                        s += f" '{n}'"
            if dr.dot == len(dr.rule.rhs):
                s += " ."
            s += f"    (start={dr.start}) {dr.values}"
            s += "\n"
    return s


def predict_and_complete[T](chart: Chart[T], g: Grammar[T], start: int):
    rules = chart[start]
    while True:
        new_rules: set[DottedRule[T]] = set()
        for dr in rules:
            match dr.dotted_sym():
                case str(x):
                    # Dot is in front of a non-terminal symbold → predict
                    for r in g:
                        if r.lhs == x:
                            new_rules.add(
                                DottedRule(rule=r, dot=0, start=start, values=ilist())
                            )
                case None:
                    # Dot is at the end → complete
                    v = dr.rule.action(*dr.values)
                    for dr2 in chart[dr.start]:
                        if dr2.dotted_sym() == dr.rule.lhs:
                            new_rules.add(
                                DottedRule(
                                    dr2.rule,
                                    dr2.dot + 1,
                                    dr2.start,
                                    dr2.values + ilist(v),
                                )
                            )
                case _:
                    # Dot is in front of a terminal symbol → nothing to do
                    pass
        old_len = len(rules)
        rules |= new_rules
        if old_len == len(rules):
            break


@dataclass
class ParseError(Exception):
    pass


@dataclass
class UnexpectedToken(ParseError):
    expected: set[str]
    token_index: int

    def __str__(self):
        return f"At token {self.token_index}, expected one of {', '.join(self.expected)}"


@dataclass
class AmbiguousParse(ParseError):
    def __str__(self):
        return "Grammar is ambiguous for this input"


@dataclass
class IncompleteParse(ParseError):
    expected: set[str]

    def __str__(self):
        return "Input is incomplete, expected one of {', '.join(self.expected)}"


def parse[T](g: Grammar[T], sym: str, s: Sequence[T], verbose: bool) -> list[Any]:
    chart: Chart[T] = [{DottedRule(r, 0, 0, ilist()) for r in g if r.lhs == sym}]

    for i, t in enumerate(s):
        predict_and_complete(chart, g, i)

        expected: set[str] = set()
        chart2: set[DottedRule[T]] = set()
        for dr in chart[i]:
            match dr.dotted_sym():
                case TokenMatcher(pred, err):
                    if pred(t):
                        chart2.add(
                            DottedRule(
                                dr.rule, dr.dot + 1, dr.start, dr.values + ilist(t)
                            )
                        )
                    else:
                        expected.add(err)
                        pass
                case _:
                    pass

        if len(chart2) == 0:
            raise UnexpectedToken(expected, i)

        chart.append(chart2)

    predict_and_complete(chart, g, len(s))

    if verbose:
        print("Earley Chart:")
        print(chart_to_str(chart))

    results: list[Any] = []
    for dr in chart[-1]:
        if dr.done() and dr.start == 0 and dr.rule.lhs == sym:
            results.append(dr.rule.action(*dr.values))

    if len(results) == 0:
        expected = set()
        for dr in chart[-1]:
            match dr.dotted_sym():
                case TokenMatcher(pred, err):
                    expected.add(err)
                case _:
                    pass
        raise IncompleteParse(expected)

    if verbose:
        print("Parse Results:")
        for r in results:
            print(f"    {r}")

    return results


def parse_unique[T](g: Grammar[T], sym: str, s: Sequence[T], verbose: bool):
    res = parse(g, sym, s, verbose)
    if len(res) > 1:
        raise AmbiguousParse()
    else:
        return res[0]
