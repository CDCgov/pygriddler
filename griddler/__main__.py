import argparse
import json
import sys

import yaml

import griddler


def main(args):
    parser = argparse.ArgumentParser(
        prog="pythom -m griddler", description="Parse a griddle into parameter sets."
    )

    parser.add_argument(
        "--from",
        "-f",
        nargs="?",
        default="yaml",
        choices=["json", "yaml"],
        metavar="FORMAT",
        dest="from_",  # to avoid collision with reserved word "from"
        help="input format (json|yaml; default: yaml)",
    )
    parser.add_argument(
        "--to",
        "-t",
        nargs="?",
        default="json",
        choices=["json", "yaml"],
        metavar="FORMAT",
        help="output format (json|yaml; default: json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        metavar="OUTPUT",
        help="output parameter sets file (default: stdout)",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        metavar="INPUT",
        help="input griddle (default: stdin)",
    )

    args = parser.parse_args(args)

    if args.from_ == "yaml":
        raw = yaml.safe_load(args.input)
    elif args.from_ == "json":
        raw = json.load(args.input)
    else:
        raise RuntimeError(f"Invalid input format {args.from_}")

    griddle = griddler.Griddle(raw)
    parameter_sets = griddle.parse()

    if args.to == "yaml":
        yaml.dump(parameter_sets, args.output)
    elif args.to == "json":
        json.dump(parameter_sets, args.output, indent=2)
    else:
        raise RuntimeError(f"Invalid output format {args.to}")


if __name__ == "__main__":
    main(args=None)
