import argparse
from bnf import BnfParser


parser = argparse.ArgumentParser()

parser.add_argument("-g", "--grammar")


def main(args):
    grammar = args.grammar
    with open(grammar, "r") as f:
        parser = BnfParser(f.read())
        parser.parse()
        print(parser.symbols)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
