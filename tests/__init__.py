import jsonschema

import griddler

schema = griddler.Griddle.load_schema()


def validate_griddle(x: dict) -> None:
    """Validate an entire griddle"""
    jsonschema.Draft202012Validator(schema).validate(x)


def validate_experiment(x: dict | list) -> None:
    """Validate the experiment inside a griddle"""
    validate_griddle({"version": "my_version", "experiment": x})
