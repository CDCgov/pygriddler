import importlib.resources
import itertools
import json
from typing import List

import jsonschema
import yaml


def load_schema() -> dict:
    with importlib.resources.open_text("griddler", "schema.json") as f:
        schema = json.load(f)

    return schema


def from_yaml(path: str) -> List[dict]:
    with open(path) as f:
        griddle = yaml.safe_load(f)

    return parse(griddle)


def from_json(path: str) -> List[dict]:
    with open(path) as f:
        griddle = json.load(f)

    return parse(griddle)


def parse(griddle: dict) -> List[dict]:
    """Convert a griddle into a list of parameter sets.

    Args:
        griddle (dict): griddle

    Returns:
        List[dict]: list of parameter sets
    """
    validate(griddle)

    # check that the `if`s are a DAG
    # this should be part of validation
    pass

    # check that varying parameter names are not repeated in the bundles
    # this should be part of validation
    pass

    # convert all the short-form varying bundles into canonical form
    pass

    # get all the varying bundles
    pass

    # make a grid of the *indices* of the unconditional bundles
    pass

    # generate parameter sets based on those indices
    pass

    # add in the unconditional fixed parameters
    pass

    # implement the conditions?
    # this might be complicated if there's a DAG

    raise NotImplementedError


def validate(griddle: dict) -> None:
    """Validate that a griddle is well-formed

    Args:
        griddle (dict): griddle

    Raises:
        jsonschema.exceptions.ValidationError: if syntactically invalid
        AssertionError: if semantically invalid
    """
    jsonschema.validate(instance=griddle, schema=load_schema())

    # griddle is a dict
    assert isinstance(griddle, dict)
    # griddle has only the known keys
    assert all(
        [
            key in ["baseline_parameters", "grid_parameters", "nested_parameters"]
            for key in griddle.keys()
        ]
    )
    # griddle has at least one of baseline or grid
    assert any(
        key in griddle.keys() for key in ["baseline_parameters", "grid_parameters"]
    )
    # can only have a nest if it has a grid
    assert (
        "nested_parameters" not in griddle.keys() or "grid_parameters" in griddle.keys()
    )
