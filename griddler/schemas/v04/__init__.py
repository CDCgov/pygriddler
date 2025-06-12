import functools
import importlib.resources
import json
from typing import Any

import jsonschema

from griddler.core import Experiment, Spec


def load_schema() -> dict:
    """Load the griddle schema from the package directory.

    Returns:
        dict: schema
    """
    with importlib.resources.open_text("griddler.schemas.v04", "schema.json") as f:
        schema = json.load(f)

    return schema


def parse(griddle: dict) -> Experiment:
    jsonschema.validate(instance=griddle, schema=load_schema())

    # confirm we are in the right schema
    assert griddle["schema"] == "v0.4"
    assert "experiment" in griddle, 'v0.4 griddle must have an "experiment" key'

    return _parse_experiment(griddle["experiment"])


def _parse_experiment(x: list[dict[str, Any]] | dict[str, Any]) -> Experiment:
    if isinstance(x, list):
        return Experiment([Spec(elt) for elt in x])
    elif isinstance(x, dict):
        assert len(x) == 1
        key, value = list(x.items())[0]
        assert isinstance(value, list)
        subexperiments = [Experiment(elt) for elt in value]
        if key == "union":
            return functools.reduce(lambda x, y: x | y, subexperiments)
        elif key == "product":
            return functools.reduce(lambda x, y: x * y, subexperiments)
        else:
            raise RuntimeError(f"Unknown experiment key: {key}")
    else:
        raise RuntimeError(f"Unknown experiment type: {x} of type {type(x)}")
