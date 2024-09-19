import yaml
import itertools


def validate(griddle: dict):
    """Validate that a griddle is well-formed

    Args:
        griddle: dictionary

    Raises:
        AssertionError: if not valid
    """
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


def parse(griddle: dict) -> list[dict]:
    """Convert a griddle into a list of parameter sets.

    Args:
        griddle: griddle

    Returns:
        list of parameter sets
    """
    validate(griddle)

    # start with the grid, and if there is no grid, consider the grid empty
    if "grid_parameters" in griddle:
        parameter_sets = [
            dict(zip(griddle["grid_parameters"].keys(), values))
            for values in itertools.product(*griddle["grid_parameters"].values())
        ]
    else:
        parameter_sets = [{}]

    # find where nested values will get merged, if they are present
    if "nested_parameters" in griddle:
        ps_nests = [
            _match_ps_nest(ps, griddle["nested_parameters"]) for ps in parameter_sets
        ]
    else:
        ps_nests = [None for ps in parameter_sets]

    # merge in baseline values, if present
    if "baseline_parameters" in griddle:
        parameter_sets = [ps | griddle["baseline_parameters"] for ps in parameter_sets]

    # update the nested values, if nests were present
    for ps, nest in zip(parameter_sets, ps_nests):
        if nest is not None:
            ps |= nest

    return parameter_sets


def _match_ps_nest(parameter_set, nests):
    """Which nest goes with this parameter set?"""
    matches = [_match_ps_nest1(parameter_set, nest) for nest in nests]
    n_matches = matches.count(True)
    if n_matches == 0:
        return None
    if n_matches == 1:
        return nests[matches.index(True)]
    else:
        raise RuntimeError(
            f"Parameter set {parameter_set} matches multiple nests: {matches}"
        )


def _match_ps_nest1(parameter_set, nest):
    """Does this parameter_set match this nest?"""
    # parameter names in common to both the ps and the nest
    common_keys = parameter_set.keys() & nest.keys()
    # are the values the same, in the ps and nest, for those common names?
    return all(nest[key] == parameter_set[key] for key in common_keys)


def read(path: str) -> list[dict]:
    """Read a griddle file, and convert to parameter sets.

    Args:
        path: path to griddle

    Returns:
        list of parameter sets
    """
    with open(path) as f:
        raw = yaml.safe_load(f)

    return parse(raw)
