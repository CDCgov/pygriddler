import itertools
from collections.abc import Iterable

from griddler.core import Experiment


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
        nests = griddle["nested_parameters"]
        unmatched_nest_idx = set(range(len(nests)))
        for ps in param_sets:
            m = _get_match(ps, nests)
            if m is not None:
                ps |= nests[m]
                unmatched_nest_idx -= {m}

        if unmatched_nest_idx:
            raise RuntimeError(
                "Nests do not match any parameter sets: ",
                *[nests[i] for i in unmatched_nest_idx],
            )

    return Experiment(param_sets)


def _get_match(param_set: dict, nests: Iterable[dict]) -> int | None:
    """
    Which nest(s) does this parameter set (i.e., Spec) match to?

    Returns: Index of the matching nest, or None if no match.
    """
    matches = [_is_match(param_set, nest) for nest in nests]

    match matches.count(True):
        case 0:
            return None
        case 1:
            return matches.index(True)
        case _:
            raise RuntimeError(f"Parameter set {param_set} matches multiple of {nests}")


def _is_match(x: dict, y: dict) -> bool:
    """
    Do these two parameter sets "match," i.e., do they have at least one parameter
    name-value pair in common?
    """
    common_keys = x.keys() & y.keys()
    return any(x[key] == y[key] for key in common_keys) if common_keys else False
