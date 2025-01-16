from dataclasses import dataclass
from util.immutable_list import IList


@dataclass(frozen=True)
class SType:
    id: str

    def __str__(self) -> str:
        return f"Type {self.id}"


@dataclass(frozen=True)
class SBType:
    id: str

    def __str__(self) -> str:
        return f"BType {self.id}"


@dataclass(frozen=True)
class SJudgement:
    id: str
    type: str

    def __str__(self) -> str:
        return f"{self.id} : {self.type}"


@dataclass(frozen=True)
class SQuery:
    id: str
    type: str

    def __str__(self) -> str:
        return f"{self.id} ? {self.type}"


@dataclass(frozen=True)
class SLearnWitnessCond:
    type: str
    func: str

    def __str__(self) -> str:
        return f"{self.type} <- {self.func}"


type Stmt = SJudgement | SQuery | SType | SBType | SLearnWitnessCond

type Program = IList[Stmt]
