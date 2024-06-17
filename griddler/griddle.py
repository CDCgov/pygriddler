import yaml
import itertools


def validate(griddle):
    """Validate that a griddle is well-formed"""
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

    return True


def parse(griddle):
    """Convert a griddle into a list of parameter sets"""
    validate(griddle)

    # start with the grid, and if there is no grid, consider the grid empty
    if "grid_parameters" in griddle:
        param_sets = [
            dict(zip(griddle["grid_parameters"].keys(), values))
            for values in itertools.product(*griddle["grid_parameters"].values())
        ]
    else:
        param_sets = [{}]

    # merge in nested values, if present
    if "nested_parameters" in griddle:
        nest_idx = [
            match_nest(nest, param_sets) for nest in griddle["nested_parameters"]
        ]

        if len(set(nest_idx)) < len(nest_idx):
            raise RuntimeError("Multiple nests match the same grid set")

        for i in nest_idx:
            param_sets[i].update(griddle["nested_parameters"][i])

    # merge in baseline values, if present
    if "baseline_parameters" in griddle:
        param_sets = [ps | griddle["baseline_parameters"] for ps in param_sets]

    return param_sets


def match_nest(nest, param_sets):
    """Which parameter set does this nest match to?"""
    matches = [_match_nest1(nest, ps) for ps in param_sets]
    n_matches = matches.count(True)
    if n_matches == 0:
        raise RuntimeError(f"Nest {nest} does not match any of {param_sets}")
    elif n_matches > 1:
        raise RuntimeError(f"Nest {nest} matches multiple of {param_sets}")

    return matches.index(True)


def _match_nest1(nest, param_set):
    """Does this nest match this parameter set?"""
    common_keys = nest.keys() & param_set.keys()
    nest_subset = {key: nest[key] for key in common_keys}
    param_subset = {key: param_set[key] for key in common_keys}
    return nest_subset == param_subset


def read(path):
    """Read a griddle file, and convert to parameter sets"""
    with open(path) as f:
        raw = yaml.load(f)

    validate(raw)
    return parse(raw)
