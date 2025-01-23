from dataclasses import dataclass, field, InitVar
from typing import Any, Callable
from py13_utils import gensym, some_condition, check_stack
from py13_records import Rec
from copy import copy


# ============ Type Classes ============

@dataclass
class TypeClass:
    name: str = gensym('T')
    cs: InitVar[dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self, cs: dict[str, Any]):
        self.comps = Rec(cs)
        self.witness_cache: list[str] = []
        self.supertype_cache: list['TypeClass'] = []
        self.witness_conditions: list[Callable[[str], bool]] = []
        self.witness_types: list['TypeClass'] = []
        self.poss = _M

    def in_poss(self, poss: 'Possibility') -> 'TypeClass':
        key = str(self)
        if poss == _M:
            poss.model[key] = self
            return self
        elif key not in poss.model:
            new = copy(self)
            new.poss = poss
            new.witness_cache = copy(new.witness_cache)
            new.supertype_cache = copy(new.supertype_cache)
            new.witness_conditions = copy(new.witness_conditions)
            new.witness_types = copy(new.witness_types)
            poss.model[key] = new
            return new
        else:
            new = poss.model[key]
            new.witness_cache = new.witness_cache + [x for x in self.witness_cache if x not in new.witness_cache]
            new.supertype_cache = new.supertype_cache + [x for x in self.supertype_cache if x not in new.supertype_cache]
            new.witness_conditions = new.witness_conditions + [x for x in self.witness_conditions if x not in new.witness_conditions]
            new.witness_types = new.witness_types + [x for x in self.witness_types if x not in new.witness_types]
            return new

    def __str__(self) -> str:
        return self.name

    def learn_witness_condition(self, c: Callable[[str], bool]):
        if c not in self.witness_conditions:
            self.witness_conditions.append(c)

    def lean_witness_type(self, T: 'TypeClass'):
        if T not in self.witness_types:
            self.witness_types.append(T)

    def validate_witness(self, a: str) -> bool:
        if not self.witness_conditions:
            return True
        if a in self.witness_cache:
            return True
        return some_condition(self.witness_conditions, a)

    def judge(self, a: str) -> bool:
        if a in self.witness_cache:
            return True
        # TODO: What is that case?
        # elif isinstance(a, str):
        #     self.witness_cache.append(a)
        #     return True
        if self.validate_witness(a):
            self.witness_cache.append(a)
            return True
        return False

    def judge_nonspec(self) -> bool:
        if self.witness_cache == []:
            self.create()
        return True

    def create(self) -> str:
        a = gensym('_a')
        self.judge(a)
        return a

    def query(self, a: str) -> str | bool:
        if check_stack("query", dict(a=a, self=self)):
            return '*'
        elif a in self.witness_cache:
            return True
        # TODO: str(self) in str(a.types) correct?
        match a:
            case HypObj(types, _) if str(self) in str(types):
                return True

# ============ Possibilities ============


@dataclass
class Possibility:
    name: str = gensym('M')
    model: dict[str, TypeClass] = field(default_factory=dict)

    def __str__(self) -> str:
        return '\n' + self.name + ':\n' + '_' * 45 + '\n' + '\n'.join([str(i) + ': ' + str(self.model[i].witness_cache) for i in self.model if i not in ['Ty', 'Re', 'RecTy']]) + '\n' + '_' * 45 + '\n'


_M = Possibility("_Model_")


def showmodel(m: Possibility = _M) -> str:
    return str(m)


def initmodel():
    global _M
    _M.model = dict()


def add_to_model():
    ...


@dataclass
class HypObj:
    types: list[TypeClass]
    name: str = gensym('h')

    # validate not needed because of type safety?
