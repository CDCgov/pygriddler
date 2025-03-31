import argparse
import json
import sys

import yaml

import griddler


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
        help="input griddle YAML (default: stdin)",
    )
    parser_parse.add_argument(
        "output",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output parameter sets JSON (default: stdout)",
    )

    args = parser.parse_args()

    if args.command == "parse":
        raw = yaml.safe_load(args.input)
        griddle = griddler.Griddle(raw)
        parameter_sets = griddle.parse()
        json.dump(parameter_sets, args.output, indent=2)
    else:
        raise RuntimeError


if __name__ == "__main__":
    run()
