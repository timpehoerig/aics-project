from itertools import count
from typing import Callable, Any
import inspect


gennum: dict[str, count[int]] = dict()


def gensym(x: str) -> str:
    """
    Create new unique identifier: xi
    """
    if x not in gennum:
        gennum[x] = count()
    return x + str(next(gennum[x]))


# TODO: What is A?
def some_condition[A](conds: list[Callable[[A], bool]], obj: A) -> bool:
    return any([f(obj) for f in conds])


def substitute(obj: Any, v: Any, a: Any) -> Any:
    match obj:
        case _ if obj == v:
            res = a
        case list():
            res = [substitute(x, v, a) for x in obj]  # type: ignore
        case tuple():
            res = tuple((substitute(x, v, a) for x in obj))  # type: ignore
        case _ if "subst" in dir(obj):
            res = obj.subst(v, a)
        case _:
            res = obj
    if res is obj or str(res) == str(obj):  # type: ignore
        return obj  # type: ignore
    return res


# ============ Tracing ============

ttracing_list: list[str] = list()


def ttrace(s: str = "all") -> list[str]:
    global ttracing_list
    if s in ttracing_list:
        pass
    elif s == "all":
        # TODO: Check if that is the same as .clear & +=
        ttracing_list = [
            'learn_witness_condition',
            'pathvalue',
            'create',
            'create_hypobj',
            'appc',
            'appc_m',
            'merge_dep_types',
            'combine_dep_types',
            'subtype_of_dep_types',
            'ti_apply'
        ]
    else:
        ttracing_list.append(s)
    return ttracing_list


def nottrace(s: str = "all") -> list[str]:
    global ttracing_list
    if s == "all":
        ttracing_list = []
    # TODO: old: "elif s in ttracing" mistake?
    elif s in ttracing_list:
        ttracing_list.remove(s)
    return ttracing_list


def ttracing(s: str) -> bool:
    return s in ttracing_list


def check_stack(f: str, argsd: dict[str, Any]) -> bool:
    frames = filter(lambda x: x[3] == f and subdict(argsd, inspect.getargvalues(x[0]).locals), inspect.stack())
    next(frames, None)
    if next(frames, None):
        return True
    return False


def subdict(d1: dict[str, Any], d2: dict[str, Any]) -> bool:
    return all(map(lambda key: key in d2 and d1[key] == d2[key], d1))


# TODO: not really necessary
def forall[A](xs: list[A], f: Callable[[A], bool]) -> bool:
    return all(map(f, xs))


def forsome[A](xs: list[A], f: Callable[[A], bool]):
    return any(map(f, xs))
