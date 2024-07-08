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
        parameter_sets = [
            dict(zip(griddle["grid_parameters"].keys(), values))
            for values in itertools.product(*griddle["grid_parameters"].values())
        ]
    else:
        parameter_sets = [{}]

    # find where nested values will get merged, if they are present
    if "nested_parameters" in griddle:
        ps_nest_map = {
            match_nest(nest, parameter_sets): nest
            for nest in griddle["nested_parameters"]
        }
    else:
        ps_nest_map = {}

    # merge in baseline values, if present
    if "baseline_parameters" in griddle:
        parameter_sets = [ps | griddle["baseline_parameters"] for ps in parameter_sets]

    # update the nested values, if nests were present
    for ps_i, nest in ps_nest_map.items():
        parameter_sets[ps_i] |= nest

    return parameter_sets


def match_nest(nest, parameter_sets):
    """Which parameter set does this nest match to?"""
    matches = [_match_nest1(nest, ps) for ps in parameter_sets]
    n_matches = matches.count(True)
    if n_matches == 0:
        return None
    if n_matches == 1:
        return matches.index(True)
    else:
        raise RuntimeError(f"Nest {nest} matches multiple of {parameter_sets}")


def _match_nest1(nest, parameter_set):
    """Does this nest match this parameter set?"""
    common_keys = nest.keys() & parameter_set.keys()
    nest_subset = {key: nest[key] for key in common_keys}
    parameter_subset = {key: parameter_set[key] for key in common_keys}
    return nest_subset == parameter_subset


def read(path):
    """Read a griddle file, and convert to parameter sets"""
    with open(path) as f:
        raw = yaml.safe_load(f)

    return parse(raw)
