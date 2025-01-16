from dataclasses import dataclass, InitVar, field
from typing import Any, Optional
from py13_utils import ttracing, substitute


@dataclass
class Rec:
    d: InitVar[dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self, d: dict[str, Any] = dict()):
        for key, value in d.items():
            match value:
                case dict():
                    self.addfield(key, Rec(value))  # type: ignore
                case _:
                    self.addfield(key, value)

    # TODO: Check if __str__ automatically does the right thing.

    def addpathl(self, pathl: list[str], value: Any) -> 'Rec':
        match pathl:
            case [path]:
                return self.addfield(path, value)
            case [path, *pathl] if path in self.__dataclass_fields__:
                val = getattr(self, path)
                match val:
                    case Rec():
                        val.addpathl(pathl, value)
                    case _:
                        print(f"{val} is not a record.")
                return self
            case [path, *pathl]:
                self.addfield(path, Rec().addpathl(pathl, value))
                return self
            case _:
                # TODO: What to do in this case?
                # Not handled in origin
                return self

    def addpath(self, path: str, value: Any) -> 'Rec':
        return self.addpathl(path.split("."), value)

    def addfield(self, label: str, value: Any) -> 'Rec':
        if label in self.__dataclass_fields__:
            print(f"'{label}' is already a label in {self}")
        else:
            setattr(self, label, value)
        return self

    def pathvalue(self, path: str) -> Any:
        splits = path.split(".")
        match splits:
            case [path]:
                if path in dir(self):
                    return getattr(self, path)
                if ttracing('pathvalue'):
                    print(f"{path} is not a label in {self}")
            case [path, *pathl]:
                if path not in dir(self) and ttracing("pathvalue"):
                    print(f"No attribute {path} in {self}")
                elif "pathvalue" not in dir(getattr(self, path)) and ttracing("pathvalue"):
                    print(f"no paths into {getattr(self, path)}")
                else:
                    return getattr(self, path).pathvalue(".".join(pathl))
            case _:
                # TODO: Not handled in origin
                pass

    # Recursive for future use
    # Needs redefining so as not to be destructive?
    def relabel(self, oldlabel: str, newlabel: str) -> 'Rec':
        newrec = Rec(self.__dict__)
        if oldlabel in newrec.__dict__.keys():
            value = newrec.__dict__[oldlabel]
            newrec.__delattr__(oldlabel)
            newrec.__setattr__(newlabel, value)
        return newrec

    def subst(self, v: Any, a: Any) -> 'Rec':
        res = Rec()
        for label in self.__dataclass_fields__:
            lval = getattr(self, label)
            match lval:
                case _ if lval == v:
                    res.addfield(label, a)
                case str():
                    res.addfield(label, lval)
                case _:
                    res.addfield(label, substitute(lval, v, a))
        return res

    def eval(self) -> 'Rec':
        for label in self.__dataclass_fields__:
            lval = getattr(self, label)
            if "eval" in dir(lval):
                setattr(self, label, lval.eval())
        return self

    def flatten(self) -> 'Rec':
        res = Rec()
        for label in self.__dataclass_fields__:
            lval = getattr(self, label)
            match lval:
                case str():
                    res.addfield(label, lval)
                case Rec():
                    rec1 = lval.flatten()
                    for label1 in rec1.__dataclass_fields__:
                        res.addfield(f"{label}.{label1}", getattr(rec1, label1))
                case _:
                    # TODO: Not handled in origin
                    pass
        return res

    def unflatten(self):
        res = Rec()
        for label in self.__dict__.keys():
            res.addpath(label, self.__getattribute__(label))
        return res

    def addrec(self, r: 'Rec') -> Optional['Rec']:
        res = Rec()
        not_contains = [label for label in self.__dataclass_fields__ if label not in r.__dataclass_fields__]
        for label in not_contains:
            res.addfield(label, getattr(self, label))

        contains = [label for label in self.__dataclass_fields__ if label in r.__dataclass_fields__]
        for label in contains:
            rl = getattr(r, label)
            sl = getattr(self, label)
            match rl, sl:
                case Rec(), Rec():
                    res1 = sl.addrec(rl)
                    if res1:
                        res.addfield(label, res1)
                    else:
                        return None
                case _ if rl == sl:
                    res.addfield(label, rl)
                case _:
                    return None

        not_conains_self = [label for label in r.__dataclass_fields__ if label not in self.__dataclass_fields__]
        for label in not_conains_self:
            res.addfield(label, getattr(r, label))
        return res
