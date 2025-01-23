from dataclasses import dataclass
from typing import Callable, Any


# ==================== Types ====================

@dataclass
class Type:
    name: str

    def __post_init__(self):
        self.witness_cache: list[Any] = list()

    def judge(self, x: Any) -> bool:
        if x not in self.witness_cache:
            self.witness_cache.append(x)
        return True

    def query(self, x: Any) -> bool:
        return x in self.witness_cache

    def __str__(self) -> str:
        return self.name


@dataclass
class BType(Type):
    name: str = "BT"

    def __post_init__(self):
        super().__post_init__()
        self.witness_condition: list[Callable[[Any], bool]] = list()

    def judge(self, x: Any) -> bool:
        if x in self.witness_cache:
            return True
        if all(map(lambda f: f(x), self.witness_condition)):
            self.witness_cache.append(x)
            return True
        return False

    def query(self, x: Any) -> bool:
        return self.judge(x)

    def learn_witness_function(self, f: Callable[[Any], bool]):
        if f not in self.witness_condition:
            self.witness_condition.append(f)


@dataclass
class PType(Type):
    name: str = "PT"

    def __post_init__(self):
        super().__post_init__()


# ==================== Models ====================

@dataclass
class Model:
    name: str


# ==================== Predicates ====================

@dataclass
class Pred:
    name: str
    arity: list[Type]

    def __post_init__(self):
        self.witness_functions: list[Callable[[Any], bool]] = list()

    def learn_witness_function(self, f: Callable[[Any], bool]):
        if f not in self.witness_functions:
            self.witness_functions.append(f)

    def __str__(self) -> str:
        return self.name


if __name__ == "__main__":
    T1 = Type("T1")
    T2 = Type("T2")
    T1.judge('a')
    T1.judge('b')
    T2.judge('b')
    T2.judge('a')

    print(T1.witness_cache)
    print(set(T1.witness_cache) == set(T2.witness_cache))
    print(T1 == T2)
