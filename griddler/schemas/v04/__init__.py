import importlib.resources
import json
from typing import Any

import jsonschema

from griddler.core import Experiment, ExperimentProduct, ExperimentUnion


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
        return Experiment(x)
    elif isinstance(x, dict):
        assert len(x) == 1
        key, value = next(iter(x.items()))
        assert isinstance(value, list)
        subexperiments = [_parse_experiment(elt) for elt in value]
        if key == "union":
            return ExperimentUnion(subexperiments)
        elif key == "product":
            return ExperimentProduct(subexperiments)
        else:
            raise RuntimeError(f"Unknown experiment key: {key}")
    else:
        raise TypeError(f"Unknown experiment type: {x} of type {type(x)}")
