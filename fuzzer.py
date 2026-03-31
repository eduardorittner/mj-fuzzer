from typing import Dict, List, Optional, TYPE_CHECKING, Union
import random
from symbols import Symbol, Terminal, NonTerminal, ProductionRule, Modifier

from bnf import BnfParser


class Fuzzer:
    """Main class for generating programs from the grammar"""

    def __init__(self, symbols: Dict[str, Symbol], max_depth: int = 10):
        """
        Initialize the fuzzer with a symbol dictionary

        :param symbols: Dictionary mapping symbol names to Symbol objects
        :param max_depth: Maximum recursion depth to prevent infinite expansion
        """
        self.symbols = symbols
        self.max_depth = max_depth

    @classmethod
    def from_bnf_parser(cls, bnf_parser: "BnfParser", max_depth: int = 10):
        """
        Create a Fuzzer instance from a BNF parser

        :param bnf_parser: BNF parser with parsed symbols
        :param max_depth: Maximum recursion depth to prevent infinite expansion
        :return: Fuzzer instance
        """
        # Combine NonTerminals and Terminals into one dictionary
        all_symbols: Dict[str, Symbol] = {}
        for name, nt in bnf_parser.symbols.items():
            all_symbols[name] = nt

        for t in bnf_parser.terminals:
            if t.name not in all_symbols:
                all_symbols[t.name] = t

        return cls(all_symbols, max_depth)

    def expand_symbol(self, symbol_name: str, depth: int = 0) -> str:
        """
        Recursively expand symbols by name to generate program text

        :param symbol_name: Name of the symbol to expand
        :param depth: Current recursion depth
        :return: Generated text representation
        """
        # Look up the symbol
        symbol = self.symbols.get(symbol_name)

        # If symbol not found, generate a reasonable default value
        if symbol is None:
            # For ID symbols, generate proper MiniJava identifiers
            if symbol_name in ["ID", "identifier"]:
                return self._generate_identifier()
            # For common expression-like symbols, generate a reasonable expression
            elif symbol_name in ["expression", "assignment_expression"]:
                return f"{random.randint(1, 100)}"
            # For literal types, generate appropriate values
            elif symbol_name == "CHAR_LITERAL":
                return f"'{chr(random.randint(97, 122))}'"  # Random lowercase letter
            elif symbol_name == "INT_LITERAL":
                return str(random.randint(0, 1000))
            elif symbol_name == "STRING_LITERAL":
                return f'"string{random.randint(1, 100)}"'
            # For boolean literals, generate true or false
            elif symbol_name == "boolean_literal":
                return random.choice(["true", "false"])
            # For other undefined symbols, treat as literal terminal
            else:
                return symbol_name

        # Check depth limit to prevent infinite recursion
        if depth > self.max_depth:
            # For terminals, still expand them even at max depth
            if isinstance(symbol, Terminal):
                return symbol.generate(self, depth + 1)
            # For non-terminals, use DFS-based approach to choose best rule
            elif isinstance(symbol, NonTerminal) and symbol.rules:
                # Choose the rule that is closest to terminal symbols
                best_rule = self._choose_best_rule_at_limit(symbol, symbol_name)
                # Generate text for this rule by continuing to expand symbols
                # Don't increment depth further when already at limit to prevent infinite recursion
                return best_rule.generate(self, depth)
            else:
                return ""

        # Generate text for the symbol
        return symbol.generate(self, depth + 1)

    def _generate_identifier(self) -> str:
        """
        Generate a proper MiniJava identifier following the rules:
        1. First character must be alphabetical
        2. Subsequent characters can be digits, alphabeticals, or underscores

        :return: Generated identifier string
        """
        # Generate first character (must be alphabetical)
        first_char = chr(random.randint(97, 122))  # Random lowercase letter a-z

        # Generate remaining characters (0-10 additional characters)
        length = random.randint(0, 10)
        remaining_chars = ""
        for _ in range(length):
            char_type = random.randint(1, 3)
            if char_type == 1:  # Digit
                remaining_chars += str(random.randint(0, 9))
            elif char_type == 2:  # Lowercase letter
                remaining_chars += chr(random.randint(97, 122))
            else:  # Underscore
                remaining_chars += "_"

        return first_char + remaining_chars

    def generate_program(self, start_symbol: str = "program") -> str:
        """
        Generate a random program from the grammar by resolving symbol names

        :param start_symbol: Name of the starting symbol (default: "program")
        :return: Generated program text
        """
        return self.expand_symbol(start_symbol, 0)

    def _calculate_distance_to_terminals(
        self, symbol_obj: Union[str, Modifier], visited: Optional[set[str]] = None
    ) -> int:
        """
        Calculate the minimum distance from a symbol to terminal symbols using DFS.

        :param symbol_obj: Name of the symbol or a Modifier to calculate distance for
        :param visited: Set of visited symbols to prevent infinite recursion
        :return: Minimum distance to terminal symbols (0 for terminals, infinity for undefined)
        """
        if visited is None:
            visited = set()

        if isinstance(symbol_obj, Modifier):
            # For modifiers, distance is the max distance of any symbol inside it
            max_dist = 0
            for inner_symbol in symbol_obj.symbols:
                dist = self._calculate_distance_to_terminals(
                    inner_symbol, visited.copy()
                )
                max_dist = max(max_dist, dist)
            return max_dist

        symbol_name = symbol_obj

        # Prevent infinite recursion
        if symbol_name in visited:
            return float("inf")

        # Look up the symbol
        symbol = self.symbols.get(symbol_name)

        # If symbol not found, return infinity (can't reach terminals)
        if symbol is None:
            # Check if it's one of the hardcoded symbols
            if symbol_name in [
                "ID",
                "identifier",
                "expression",
                "assignment_expression",
                "CHAR_LITERAL",
                "INT_LITERAL",
                "STRING_LITERAL",
                "boolean_literal",
            ]:
                return 0
            return float("inf")

        # For terminals, distance is 0
        if isinstance(symbol, Terminal):
            return 0

        # For non-terminals, calculate minimum distance through all rules
        if isinstance(symbol, NonTerminal) and symbol.rules:
            visited.add(symbol_name)
            min_distance = float("inf")

            # For each rule, calculate the maximum distance through its symbols
            # (since all symbols in a rule must be expanded)
            for rule in symbol.rules:
                max_rule_distance = 0
                for rule_symbol in rule.symbols:
                    # Calculate distance for this symbol and add 1 for the expansion step
                    distance = (
                        self._calculate_distance_to_terminals(
                            rule_symbol, visited.copy()
                        )
                        + 1
                    )
                    # Take the maximum distance in this rule (worst case)
                    max_rule_distance = max(max_rule_distance, distance)
                # Take the minimum distance across all rules (best choice)
                min_distance = min(min_distance, max_rule_distance)

            visited.remove(symbol_name)
            return min_distance if min_distance != float("inf") else float("inf")

        # For undefined symbols, return infinity
        return float("inf")

    def _choose_best_rule_at_limit(
        self, symbol: NonTerminal, symbol_name: str
    ) -> ProductionRule:
        """
        Choose the best rule when at depth limit using DFS-based approach.

        :param symbol: The non-terminal symbol
        :param symbol_name: Name of the symbol (for cycle detection)
        :return: The best production rule to use
        """
        if not symbol.rules:
            raise ValueError("Non-terminal has no rules")

        # Calculate distance to terminals for each rule
        rule_distances = []
        for rule in symbol.rules:
            max_distance = 0
            for rule_symbol in rule.symbols:
                distance = self._calculate_distance_to_terminals(rule_symbol)
                max_distance = max(max_distance, distance)
            rule_distances.append(max_distance)

        # Choose the rule with the minimum distance to terminals
        # If multiple rules have the same distance, choose one randomly
        min_distance = min(rule_distances)
        best_rules = [
            rule
            for rule, distance in zip(symbol.rules, rule_distances)
            if distance == min_distance
        ]

        # If all rules have infinite distance, fall back to simplest rule
        if min_distance == float("inf"):
            return min(symbol.rules, key=lambda r: len(r.symbols))

        # Return a random rule among the best ones
        return random.choice(best_rules)

    def generate_ast(self, start_symbol: str = "program"):
        """
        Generate an AST from the grammar that matches compiler output

        :param start_symbol: Name of the starting symbol (default: "program")
        :return: Generated AST representation
        """
        # For now, we'll create a simple AST node with the generated program text
        # In a more complete implementation, we would generate a full AST structure
        program_text = self.generate_program(start_symbol)
        return {"type": "Program", "source": program_text}
