import itertools
from collections.abc import Iterable

from griddler.core import Experiment, Spec


def _validate(griddle: dict) -> None:
    """Validate that a griddle is well-formed"""
    # griddle is a dict
    assert isinstance(griddle, dict)
    # griddle has only the known keys
    if bad_keys := set(griddle.keys()) - {
        "schema",
        "baseline_parameters",
        "grid_parameters",
        "nested_parameters",
    }:
        raise RuntimeError(f"Griddle has unknown keys: {bad_keys}")

    # griddle has at least one of baseline or grid
    assert any(
        key in griddle.keys() for key in ["baseline_parameters", "grid_parameters"]
    )

    # can only have a nest if it has a grid
    assert (
        "nested_parameters" not in griddle.keys() or "grid_parameters" in griddle.keys()
    )


def parse(griddle: dict) -> Experiment:
    _validate(griddle)

    # start with the grid, and if there is no grid, consider the grid empty
    if "grid_parameters" in griddle:
        param_sets = [
            dict(zip(griddle["grid_parameters"].keys(), values))
            for values in itertools.product(*griddle["grid_parameters"].values())
        ]
    else:
        param_sets = [{}]

    # merge in baseline values, if present
    if "baseline_parameters" in griddle:
        param_sets = [ps | griddle["baseline_parameters"] for ps in param_sets]

    # find where nested values will get merged, if they are present
    if "nested_parameters" in griddle:
        for nest in griddle["nested_parameters"]:
            m = _match_nest(nest, param_sets)
            param_sets[m] |= nest

    return Experiment([Spec(ps) for ps in param_sets])


def _match_nest(nest: dict, param_sets: Iterable[dict]) -> int:
    """Which parameter set does this nest match to?"""
    matches = [_match_nest1(nest, ps) for ps in param_sets]
    n_matches = matches.count(True)
    if n_matches == 0:
        raise RuntimeError(
            f"Nest {nest} does not match any parameter set in {param_sets}"
        )
    elif n_matches == 1:
        return matches.index(True)
    else:
        raise RuntimeError(f"Nest {nest} matches multiple of {param_sets}")


def _match_nest1(nest: dict, param_set: dict) -> bool:
    """
    Does this nest match this parameter set?

    A nest matches a parameter set if there is at least one parameter name-value
    combination in common.
    """
    common_keys = nest.keys() & param_set.keys()
    return (
        any(nest[key] == param_set[key] for key in common_keys)
        if common_keys
        else False
    )
