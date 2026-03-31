from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, TYPE_CHECKING, Union
import random

if TYPE_CHECKING:
    from fuzzer import Fuzzer


class Symbol:
    """Base class for all symbols in the grammar"""

    def generate(self, fuzzer: "Fuzzer", depth: int = 0) -> str:
        """Generate text representation of this symbol"""
        raise NotImplementedError


class ModifierType(Enum):
    ZERO_OR_ONE = "?"
    ZERO_OR_MORE = "*"
    ONE_OR_MORE = "+"


@dataclass
class Modifier(Symbol):
    """Represents a modifier (*, ?, +) for a list of symbols"""

    type: ModifierType
    symbols: List[str]

    def generate(self, fuzzer: "Fuzzer", depth: int = 0) -> str:
        """Generate text representation for this modifier"""
        repetitions = 0
        if self.type == ModifierType.ZERO_OR_ONE:
            repetitions = random.randint(0, 1)
        elif self.type == ModifierType.ZERO_OR_MORE:
            repetitions = random.randint(0, 5)  # Limit to 5 to avoid too large output
        elif self.type == ModifierType.ONE_OR_MORE:
            repetitions = random.randint(1, 5)

        results = []
        for _ in range(repetitions):
            for symbol_name in self.symbols:
                results.append(fuzzer.expand_symbol(symbol_name, depth + 1))

        return " ".join(filter(None, results))


@dataclass
class ProductionRule(Symbol):
    """Represents a production rule with a list of symbol names or modifiers"""

    symbols: List[Union[str, Modifier]]

    def generate(self, fuzzer: "Fuzzer", depth: int = 0) -> str:
        """Generate text representation of this production rule"""
        result = []
        for symbol in self.symbols:
            if isinstance(symbol, Modifier):
                content = symbol.generate(fuzzer, depth)
                if content:
                    result.append(content)
            else:
                content = fuzzer.expand_symbol(symbol, depth + 1)
                if content:
                    result.append(content)
        return " ".join(result)


@dataclass(frozen=True)
class Terminal(Symbol):
    """Represents a terminal symbol in the grammar"""

    name: str
    is_token: bool = False

    def generate(self, fuzzer: "Fuzzer", depth: int = 0) -> str:
        """Generate text representation of this terminal"""
        if self.is_token:
            return fuzzer.expand_symbol(self.name, depth)
        return self.name


@dataclass
class NonTerminal(Symbol):
    """Represents a non-terminal symbol with production rules"""

    name: str
    rules: List[ProductionRule]

    def generate(self, fuzzer: "Fuzzer", depth: int = 0) -> str:
        """Generate text representation of this non-terminal"""
        if not self.rules:
            return ""

        # Choose a random production rule
        rule = random.choice(self.rules)
        return rule.generate(fuzzer, depth + 1)
