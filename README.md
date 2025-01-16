# An interpreter for PyTTR

This is an interpreter for PyTTR.

## Table of Contents
1. [Introduction](#introduction)
2. [Usage](#usage)
    1. [Command Line](#command-line)
    2. [Direct Import](#direct-import)
3. [A basics tour](#a-basics-tour)
    1. [Basic Type](#basic-types)
    2. [Witness Conditions](#witness-conditions)
4. [Implementation details](#implementation-details)
    1. [Utils](#util)
    2. [PyTTR AST](#pyttr-ast)
    3. [Lexer](#lexer)
    4. [Parser](#parser)
    5. [Interpreter](#interpreter)
    6. [Run](#run)
    7. [PyTTR](#pyttr)

## Introduction

PyTTR is an implementation of Type Theory with Records in Python.

As the current implementation is in Python3.4, and furthermore the Syntax of using it is very verbose.
This provides and Interpreter for PyTTR with a simple and easy to change syntax that parses a PyTTR program and translates it to the current implementation and executes it.

As this is only a very short project, the PyTTR program is not translated to the real current implementation but to and subset of that, which is implemented in the most current Python3.13 version.

Extending this subset to the full scope of the current implementation is straight forward but time consuming and thus is not done in the scope of that project.

This is a basic program in the current implementation of PyTTR:

```py
T = Type()
T.judge('a')

print(T.query('a'))
```

And this is the same program with the new interpreter:

```py
Type T
a : T

a ? T
```

## Usage

The accespoint to this package is the `run` file.

*DISCLAIMER: You may have to change `run` to the full path. And/or change it so it fits your os.*

There are 2 ways to use this package:

### Command Line

You can use the command line to execute the interpreter directly on a file.

```shell
usage: python3.13 ./py13/run.py path
```

positional arguments:

    path             The file your PyTTR program is in.

### Direct Import

In order to use this package directly in Python, 4 imports are required:

```py
from run import read
from lexer import lex
from parser import parse
from interpreter import interprete
```

The `read` function takes a path to a file an returns it input as a `string`.

The `lex` function takes a pyttr program as a `string` and returns a list of Tokens.

The `parse` function takes a list of Tokens and returns a pyttr `Program`.

The `interprete` function takes a pyttr `Program` and interpretes it. The output is printed.

*In order to use the output of the interprete function, the interpreter.py file must be changed st. it does not print, but returns the output strings.*

## A Basics Tour

### Basic Types

Old:
```py
T = Type()
T.judge('a')

print(T.query('a'))
```

New:
```py
BType Ind
a : Ind
```

### Witness Conditions

Old:
```py
Real = BType('Real')
Real.learn_witness_condition(lambda n: isinstance(n,float))

print(Real.query(0.5))
```

New:
```py
BType Real
Real <- lambda n: isinstance(n, float)

0.5 ? Real
```

## Implementation Details

The package structure is as following:

```
<Project>
├── py13
└── origin
```

The files in `origin` are updated versions of the full current PyTTR implementation. Both `records` and `utils` are fully functional, while `ttrtypes` is only started. While working on them I noticed completely redoing them is too much for the scope of this project. However, I think it can still be of interest for future work to have them somewhere around.

In `py13` lays the heart of this project:

```
<Py13>
├── util
├── py13_pyttr_AST.py
├── lexer.py
├── parser.py
├── interpreter.py
├── py13_pyttr.py
└── run.py
```

### Util

As I could not find a fitting parser library for python13.3 util contains an own parser library.
Furthermore, util contains an implementation of an immutable List.

### PyTTR AST

```
Dependencies:
    dataclass from dataclasses
    from util.immutable_list import IList
```

Every object in PyTTR is represented by a dataclass:

1. `Type`
2. `BType`
3. `Judgement`
4. `Query`
5. `LearnWitnessCond`

### lexer

Specifies tokens for all tokens in the PyTTR language. It is easily extendable.

### parser

Translates tokens from [lexer](#lexer) to an AST from [PyTTR AST](#PyTTR-AS)

### interpreter

Tanslates the [PyTTR AST](#pyttr-ast) to the corresponding calls in [pyttr](#pyttr)

### run

Runs [interprete](#interpreter) on a given file.

### pyttr

A subset of the current PyTTr implementation translated to python3.13.
