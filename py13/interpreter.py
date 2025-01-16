from py13_pyttr_AST import *
from py13_pyttr import *


def parse(s: str) -> Any:
    if s.isalpha():
        return s
    return eval(s)


def interprete_stmt(env: dict[str, Type], stmt: Stmt):
    match stmt:
        case SType(id):
            t = Type(id)
            env[id] = t
            print(f"Type {t}")
        case SBType(id):
            t = BType(id)
            env[id] = t
            print(f"BType {t}")
        case SJudgement(id, type):
            t = env[type]
            res = t.judge(parse(id))
            print(f"{id} : {t} -> {res}")
        case SQuery(id, type):
            t = env[type]
            res = t.query(parse(id))
            print(f"{id} ? {t} -> {res}")
        case SLearnWitnessCond(type, func):
            t = env[type]
            match t:
                case BType():
                    t.learn_witness_function(eval(func))
                case _:
                    raise Exception("Tried to learn a witness condition on non BType")


def interprete(p: Program):
    env: dict[str, Type] = dict()
    for stmt in p:
        interprete_stmt(env, stmt)
