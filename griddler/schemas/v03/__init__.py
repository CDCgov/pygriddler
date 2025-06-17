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
    with importlib.resources.open_text("griddler.schemas.v03", "schema.json") as f:
        schema = json.load(f)

    return schema


def parse(griddle: dict) -> Experiment:
    jsonschema.validate(instance=griddle, schema=load_schema())

    # confirm we are in the right schema
    assert griddle["schema"] == "v0.3"
    assert "parameters" in griddle, 'v0.3 griddle must have an "parameters" key'

    return _parse_parameters(griddle["parameters"])


def _parse_parameters(parameters: dict[str, Any]) -> Experiment:
    # start with an empty experiment
    ex = Experiment([Spec({})])

    # call everything a bundle at first
    for bundle_name, bundle_value in parameters.items():
        assert isinstance(bundle_value, dict)
        if "fix" in bundle_value:
            if "if" in bundle_value:
                fix_spec = Spec({bundle_name: bundle_value["fix"]})
                for spec in ex.specs:
                    if _if_match(spec, bundle_value["if"]):
                        # if the condition matches, add the fixed value
                        spec |= fix_spec
                        spec[bundle_name] = bundle_value["fix"]
            else:
                # add this value to every Spec in the Experiment
                fix_ex = Experiment([Spec({bundle_name: bundle_value["fix"]})])
                ex *= fix_ex
        elif "vary" in bundle_value:
            vary_ex = Experiment([Spec({bundle_name: x}) for x in bundle_value["vary"]])
            ex *= vary_ex
        else:
            # this is a bundle
            lens = [len(x) for x in bundle_value.values()]
            assert len(set(lens)) == 1, "All bundle values must have the same length"
            # make an experiment where each Spec has each parameter, and all the values
            # of those parameters are matched within the Spec
            bundle_ex = Experiment(
                [
                    Spec({k: bundle_value[k][i] for k in bundle_value.keys()})
                    for i in range(lens[0])
                ]
            )
            ex *= bundle_ex

    return ex


def _if_match(spec: Spec, condition: dict[str, Any]) -> bool:
    """Check if a Spec matches a condition.

    Args:
        spec (Spec): The Spec to check.
        condition (dict[str, Any]): The condition to match against.

    Returns:
        bool: True if the Spec matches the condition, False otherwise.
    """
    assert isinstance(condition, dict), "Condition must be a dictionary"
    assert "equals" in condition, "Only 'equals' conditions are supported"
    assert len(condition["equals"]) == 1, (
        "Only one key is allowed in 'equals' condition"
    )

    if_name = condition["equals"].keys()[0]
    if_value = condition["equals"][if_name]

    return if_name in spec and spec[if_name] == if_value
