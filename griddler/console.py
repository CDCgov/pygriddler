import griddler.griddle
import argparse
import sys
import yaml


def run():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", required=True)

    parser_parse = subparsers.add_parser("parse", help="parse a griddle")
    parser_parse.set_defaults(command="parse")
    parser_parse.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input griddle",
    )
    parser_parse.add_argument(
        "output",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output parameter sets yaml",
    )

    args = parser.parse_args()

    if args.command == "parse":
        raw = yaml.safe_load(args.input)
        parameter_sets = griddler.griddle.parse(raw)
        yaml.dump(parameter_sets, args.output)
    else:
        raise RuntimeError


if __name__ == "__main__":
    run()
