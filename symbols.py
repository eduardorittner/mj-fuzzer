from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from fuzzer import Fuzzer


class Symbol:
    """Base class for all symbols in the grammar"""
    def generate(self, fuzzer: 'Fuzzer', depth: int = 0) -> str:
        """Generate text representation of this symbol"""
        raise NotImplementedError


@dataclass
class ProductionRule(Symbol):
    """Represents a production rule with a list of symbol names"""
    symbols: List[str]
    
    def generate(self, fuzzer: 'Fuzzer', depth: int = 0) -> str:
        """Generate text representation of this production rule"""
        result = ""
        for symbol_name in self.symbols:
            # Add space between symbols for readability
            if result:
                result += " "
            result += fuzzer.expand_symbol(symbol_name, depth + 1)
        return result


@dataclass
class Terminal(Symbol):
    """Represents a terminal symbol in the grammar"""
    name: str
    
    def generate(self, fuzzer: 'Fuzzer', depth: int = 0) -> str:
        """Generate text representation of this terminal"""
        return self.name


@dataclass
class NonTerminal(Symbol):
    """Represents a non-terminal symbol with production rules"""
    name: str
    rules: List[ProductionRule]
    
    def generate(self, fuzzer: 'Fuzzer', depth: int = 0) -> str:
        """Generate text representation of this non-terminal"""
        if not self.rules:
            return ""
        
        # Choose a random production rule
        rule = random.choice(self.rules)
        return rule.generate(fuzzer, depth + 1)
