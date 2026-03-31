from bnf import BnfParser
from symbols import ModifierType, ProductionRule


def test_rule_name_parsing():
    parser = BnfParser("<hello> world!")

    rule = parser.rule_name()
    assert rule == "hello"
    assert parser.input == " world!"


def test_assignment_parsing():
    parser = BnfParser("hello ::= world")

    parser.assignment()
    assert parser.input == "world"


def test_terminal_parsing():
    parser = BnfParser('"{" other symbols')

    terminal = parser.terminal()
    assert terminal == "{"
    assert parser.input == " other symbols"


def test_production_rule():
    parser = BnfParser('"terminal" <non-terminal>\n<not-parsed>')

    first_rule = parser.production_rule()
    assert first_rule.symbols == [
        "terminal",
        "non-terminal",
    ]

    assert parser.input == "<not-parsed>"


def test_production_rules():
    parser = BnfParser('"terminal" <non-terminal>\n| <second-rule>\nother-thing')

    rules = parser.production_rules()

    assert 2 == len(rules)

    assert rules[0].symbols == [
        "terminal",
        "non-terminal",
    ]
    assert rules[1].symbols == ["second-rule"]
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
        "terminal",
        "non-terminal",
    ]
    assert rule.rules[1].symbols == ["other-terminal"]
    assert parser.input == ""
    assert parser.symbols["rule-name"] == rule


def test_parse_modifier():
    parser = BnfParser('{<hello> "world!"}*')

    modifier = parser.modifier()

    assert modifier.symbols[0] == "hello"
    assert modifier.symbols[1] == "world!"
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
        "terminal",
        "non-terminal",
    ]
    assert parser.symbols["rule1"].rules[1].symbols == ["other-terminal"]
    assert parser.symbols["rule2"].rules[0].symbols == [
        "hello",
        ", ",
        "world",
    ]


def test_actual_grammar():
    with open("mj.bnf", "r") as f:
        parser = BnfParser(f.read())
        parser.parse()


def test_token_terminal_recognition():
    parser = BnfParser('<rule> ::= <INT_LITERAL> | <ID>\n<ID> ::= "id"')
    parser.parse()

    # INT_LITERAL should be a terminal with is_token=True
    int_terminal = [t for t in parser.terminals if t.name == "INT_LITERAL"][0]
    assert int_terminal.is_token is True

    # ID should NOT be in terminals because it is defined as a rule
    id_terminals = [t for t in parser.terminals if t.name == "ID"]
    assert len(id_terminals) == 0
    assert "ID" in parser.symbols
