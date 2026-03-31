from bnf import BnfParser
from bnf_ast import *


def test_rule_name_parsing():
    parser = BnfParser("<hello> world!")

    rule = parser.rule_name()
    assert rule.name == "hello"
    assert parser.input == " world!"


def test_assignment_parsing():
    parser = BnfParser("hello ::= world")

    parser.assignment()
    assert parser.input == "world"


def test_terminal_parsing():
    parser = BnfParser('"{" other symbols')

    terminal = parser.terminal()
    assert terminal.name == "{"
    assert parser.input == " other symbols"


def test_production_rule():
    parser = BnfParser('"terminal" <non-terminal>\n<not-parsed>')

    first_rule = parser.production_rule()
    assert first_rule.symbols == [
        SymbolReference("terminal", SymbolType.TERMINAL),
        SymbolReference("non-terminal", SymbolType.NONTERMINAL),
    ]

    assert parser.input == "<not-parsed>"


def test_production_rules():
    parser = BnfParser('"terminal" <non-terminal>\n| <second-rule>\nother-thing')

    rules = parser.production_rules()

    assert 2 == len(rules)

    assert rules[0].symbols == [
        SymbolReference("terminal", SymbolType.TERMINAL),
        SymbolReference("non-terminal", SymbolType.NONTERMINAL),
    ]
    assert rules[1].symbols == [SymbolReference("second-rule", SymbolType.NONTERMINAL)]
    assert parser.input == "other-thing"


def test_rule():
    parser = BnfParser(
        """
    <rule-name> ::= "terminal" <non-terminal>
                  | "other-terminal"
    """
    )

    rule = parser.rule()

    assert rule.name == "rule-name"
    assert 2 == len(rule.rules)

    assert rule.rules[0].symbols == [
        SymbolReference("terminal", SymbolType.TERMINAL),
        SymbolReference("non-terminal", SymbolType.NONTERMINAL),
    ]
    assert rule.rules[1].symbols == [
        SymbolReference("other-terminal", SymbolType.TERMINAL)
    ]
    assert parser.input == ""
    assert parser.symbols["rule-name"] == rule


def test_parse_modifier():
    parser = BnfParser('{<hello> "world!"}*')

    modifier = parser.modifier()

    assert modifier.symbols[0] == SymbolReference("hello", SymbolType.NONTERMINAL)
    assert modifier.symbols[1] == SymbolReference("world!", SymbolType.TERMINAL)
    assert modifier.type == ModifierType.ZERO_OR_MORE


def test_parse_full():
    parser = BnfParser(
        """
    <rule1> ::= "terminal" <non-terminal>
                  | "other-terminal"
    <rule2> ::= <hello> ", " <world>
    """
    )

    parser.parse()

    assert parser.symbols["rule1"].rules[0].symbols == [
        SymbolReference("terminal", SymbolType.TERMINAL),
        SymbolReference("non-terminal", SymbolType.NONTERMINAL),
    ]
    assert parser.symbols["rule1"].rules[1].symbols == [
        SymbolReference("other-terminal", SymbolType.TERMINAL),
    ]
    assert parser.symbols["rule2"].rules[0].symbols == [
        SymbolReference("hello", SymbolType.NONTERMINAL),
        SymbolReference(", ", SymbolType.TERMINAL),
        SymbolReference("world", SymbolType.NONTERMINAL),
    ]


def test_actual_grammar():
    with open("mj.bnf", "r") as f:
        parser = BnfParser(f.read())
        parser.parse()
