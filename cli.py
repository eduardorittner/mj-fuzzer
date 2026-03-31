import argparse
import subprocess
import sys
from bnf import BnfParser
from fuzzer import Fuzzer


def main():
    """Main entry point for the fuzzer CLI"""
    parser = argparse.ArgumentParser(description="MiniJava Fuzzer")
    parser.add_argument(
        "--grammar", "-g", default="mj.bnf", help="Path to the BNF grammar file"
    )
    parser.add_argument(
        "--output", "-o", help="Output file for generated program (default: stdout)"
    )
    parser.add_argument(
        "--depth",
        "-d",
        type=int,
        default=10,
        help="Maximum recursion depth (default: 10)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of programs to generate (default: 1)",
    )
    parser.add_argument(
        "--command",
        "-c",
        type=str,
        help="Command to call the compiler",
    )
    parser.add_argument(
        "--ast", action="store_true", help="Generate AST instead of source code"
    )

    args = parser.parse_args()

    try:
        # Read the grammar file

        with open(args.grammar, "r") as f:
            bnf_text = f.read()

        # Parse the grammar
        bnf_parser = BnfParser(bnf_text)
        bnf_parser.parse()

        # Create fuzzer
        fuzzer = Fuzzer.from_bnf_parser(bnf_parser, max_depth=args.depth)

        # Generate programs
        for i in range(args.count):
            if args.ast:
                # Generate AST using the fuzzer's built-in method
                ast = fuzzer.generate_ast()
                output = str(ast)
            else:
                # Generate source code
                output = fuzzer.generate_program()

            # Output the result
            if args.command:
                if args.output:
                    with open(args.output, "w") as f:
                        f.write(output)
                    subprocess.run(args.command, capture_output=True)
                else:
                    raise ValueError("Need output file in order to call compiler")
            else:
                if args.output:
                    with open(args.output, "w") as f:
                        f.write(output)
                else:
                    if args.count > 1:
                        print(f"--- Program {i+1} ---")
                    print(output)

    except FileNotFoundError:
        print(f"Error: Grammar file '{args.grammar}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
