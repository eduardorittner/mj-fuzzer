from enum import Enum
from dataclasses import dataclass


class Symbol:
    pass


class SymbolType(Enum):
    TERMINAL = 1
    NONTERMINAL = 2


@dataclass
class SymbolReference:
    name: str
    ty: SymbolType


@dataclass
class Rule:
    symbols: list[SymbolReference]


# frozen=True needed for Terminal to be hashable
@dataclass(frozen=True)
class Terminal(Symbol):
    name: str


@dataclass
class NonTerminal(Symbol):
    name: str
    rules: list[Rule]


class ModifierType(Enum):
    ZERO_OR_ONE = "?"
    ZERO_OR_MORE = "*"
    ONE_OR_MORE = "+"


@dataclass
class Modifier:
    type: ModifierType
    symbols: list[SymbolReference]
