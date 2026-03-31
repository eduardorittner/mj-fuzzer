from symbols import NonTerminal, Terminal, ProductionRule, Modifier, ModifierType
from typing import Dict, List, Set, Union


class BnfParser:
    def __init__(self, source: str):
        self.source = source
        self.input = source
        self.symbols: Dict[str, NonTerminal] = {}
        self.terminals: set[Terminal] = set([])

    def parse(self):
        """Main parsing function to process the entire grammar"""
        return self.parse_all_rules()

    def parse_all_rules(self):
        """Parse all rules in the grammar file"""
        rules = []
        while self.input.strip():
            # Skip empty lines and whitespace
            self.input = self.input.lstrip()
            if not self.input:
                break

            # Check if we have a rule (starts with <)
            if self.input[0] == "<":
                rule = self.rule()
                rules.append(rule)
                self.symbols[rule.name] = rule
            else:
                # Skip any non-rule content
                line_end = self.input.find("\n")
                if line_end == -1:
                    break
                self.input = self.input[line_end + 1 :]

        return rules

    def modifier(self) -> Modifier:
        if self.input[0] != "{":
            raise ValueError("Modifier should start with '{'")

        self.input = self.input[1:]

        symbols = []

        while self.input[0] != "}":
            self.input = self.input.lstrip()
            if self.input[0] == "<":
                symbols.append(self.rule_name())
            elif self.input[0] == '"':
                symbols.append(self.terminal())
            else:
                raise ValueError("expected symbol")

        self.input = self.input[1:]

        if self.input[0] == "*":
            self.input = self.input[1:]
            return Modifier(ModifierType.ZERO_OR_MORE, symbols)
        elif self.input[0] == "?":
            self.input = self.input[1:]
            return Modifier(ModifierType.ZERO_OR_ONE, symbols)
        elif self.input[0] == "+":
            self.input = self.input[1:]
            return Modifier(ModifierType.ONE_OR_MORE, symbols)
        else:
            raise ValueError("Modifier should end with '*', '?' or '+'")

    def rule_name(self) -> str:
        if self.input[0] != "<":
            raise ValueError("Rule name must start with '<'")

        end = self.input.find(">", 1)

        rule_name = self.input[1:end]
        self.input = self.input[end + 1 :]

        # If the rule name is all uppercase, it's a special terminal token
        if rule_name.isupper():
            # Check if this name has been defined as a non-terminal already
            if self.symbols.get(rule_name) is None:
                self.terminals.add(Terminal(rule_name, is_token=True))

        return rule_name

    def assignment(self):
        pattern = "::="
        start = self.input.find(pattern)
        self.input = self.input[start + len(pattern) :].lstrip()

    def rule(self) -> NonTerminal:
        self.input = self.input.lstrip()
        name = self.rule_name()
        self.assignment()
        rules = self.production_rules()

        rule = NonTerminal(name, rules)

        if self.symbols.get(name) is None:
            self.symbols[name] = rule

        # Remove it from terminals if it was previously added as a token terminal
        self.terminals = {t for t in self.terminals if t.name != name}

        return rule

    def terminal(self) -> str:
        if self.input[0] != '"':
            raise ValueError("Terminal should start with '\"'")

        self.input = self.input[1:]

        end = self.input.find('"')
        name = self.input[:end]
        self.input = self.input[end + 1 :]

        # Create terminal symbol if it doesn't exist
        # Note: we use the name as the key and a Terminal object
        # but in production rules we just use the name string
        if self.symbols.get(name) is None:
            self.terminals.add(Terminal(name))

        return name

    def production_rules(self) -> List[ProductionRule]:
        rules = []

        while True:
            self.input = self.input.lstrip()
            if not self.input or (self.input[0] not in ['"', "<", "|", "{"]):
                break

            if self.input[0] == "|":
                self.input = self.input[1:].lstrip()

            rules.append(self.production_rule())

            # Check if there are more production rules (indicated by |)
            self.input = self.input.lstrip()
            if not self.input or self.input[0] != "|":
                break

        return rules

    def production_rule(self) -> ProductionRule:
        symbols: List[Union[str, Modifier]] = []

        # Process symbols until we reach the end of the rule
        while self.input and self.input[0] not in ["\n", "\r", "|"]:
            self.input = self.input.lstrip()
            if not self.input:
                break

            if self.input[0] == '"':
                symbols.append(self.terminal())
            elif self.input[0] == "<":
                symbols.append(self.rule_name())
            elif self.input[0] == "{":
                symbols.append(self.modifier())
            else:
                break  # might be end of rule or unexpected char

        # Skip to the end of the line
        line_end = self.input.find("\n")
        if line_end != -1:
            self.input = self.input[line_end + 1 :]
        else:
            self.input = ""

        return ProductionRule(symbols)
