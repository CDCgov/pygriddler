import importlib.resources
import json
import uuid
from typing import Any, List

import jsonschema
import networkx as nx
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
    # do syntactic validation
    jsonschema.validate(instance=griddle, schema=load_schema())

    # check for version
    assert griddle["version"] == "v0.3", "Only v0.3 griddles are supported"

    # extract the parameters section of the griddle
    params = griddle["parameters"]
    assert isinstance(params, dict)

    return _parse_params(params)


def _parse_params(params: dict) -> List[dict]:
    """Parse the parameters section of the griddle"""
    # check that no parameter names are repeated
    _validate_parameter_names(params)

    # convert parameter specifications to canonical form
    params = _to_canonical_form(params)

    # determine the order in which we'll add parameters to the parameter sets
    param_order = _get_param_order(params)

    # initialize the output parameter sets
    parameter_sets = [{}]

    for name in param_order:
        spec = params[name]

        new_parameter_sets = []

        while parameter_sets:
            ps = parameter_sets.pop(0)

            # check if the `if` condition is satisfied
            assert "if" in spec
            if _eval_condition(spec["if"], ps):
                # if this is a fixed parameter, add it
                if "fix" in spec:
                    ps[name] = spec["fix"]
                    new_parameter_sets.append(ps)
                # if this is a varying parameter, add new values
                elif "vary" in spec:
                    # get the length of the
                    ns = [len(values) for values in spec["vary"].values()]
                    assert len(set(ns)) == 1, (
                        f"Varying parameters in bundle {name} must have the same number of values"
                    )
                    n = ns[0]
                    for i in range(n):
                        this_ps = ps.copy()
                        for vary_name, vary_values in spec["vary"].items():
                            this_ps[vary_name] = vary_values[i]
                        new_parameter_sets.append(this_ps)

        parameter_sets = new_parameter_sets

    return parameter_sets


def _get_param_order(params: dict) -> List[str]:
    """Get the order of parameters in the griddle, using the DAG of `if`s.

    Args:
        ps (dict): dictionary of name: specification

    Returns:
        List[str]: order of parameters
    """
    # create a directed graph from the `if`s
    G = nx.DiGraph()
    for name, spec in params.items():
        G.add_node(name)

        # if this parameter depends on other ones, add edges from
        # those parameters to this one
        assert "if" in spec
        for cond_name in _condition_depends_on(spec["if"]):
            G.add_edge(cond_name, name)

    # confirm this graph is a DAG
    if not nx.is_directed_acyclic_graph(G):
        raise RuntimeError("The `if` conditions form a cycle.")

    # get the topological sort of the graph
    return list(nx.topological_sort(G))


def _validate_parameter_names(params: dict) -> None:
    """Check that there are no name collisions, especially with the varying
    bundles.

    Args:
        params (dict): dictionary of name: specification
    """
    names = []
    for name, spec in params.items():
        if "fix" in spec:
            assert name not in names, f"Duplicate parameter name: {name}"
            names.append(name)
        elif "vary" in spec and isinstance(spec["vary"], dict):
            # this is a canonical form bundle
            for in_bundle_name in spec["vary"].keys():
                assert in_bundle_name not in names, (
                    f"Duplicate parameter name(s): {in_bundle_name}"
                )
                names.extend(in_bundle_name)
        elif "vary" in spec and isinstance(spec["vary"], list):
            # this is a short-form bundle
            assert name not in names, f"Duplicate parameter name: {name}"
            names.append(name)
        else:
            raise RuntimeError(f"Unknown parameter specification: {name}: {spec}")


def _to_canonical_form(params: dict[str, Any]) -> dict[str, Any]:
    """Convert parameter specifications into canonical form, including:

    - Ensure `if` conditions for all parameters & bundles
    - Change single-variable varying into bundles

    Args:
        params (dict): parameter specifications

    Returns:
        dict: canonical form
    """
    out = {}

    # convert short-forms to bundles
    for name, spec in params.items():
        if "vary" in spec and isinstance(spec["vary"], list):
            # generate an ad hoc bundle name
            bundle_name = str(uuid.uuid4())
            out[bundle_name] = {"vary": {name: spec["vary"]}}

            if "if" in spec:
                out[bundle_name]["if"] = spec["if"]
        else:
            out[name] = spec

    # add `if` if absent
    for name in out.keys():
        if "if" not in out[name]:
            out[name]["if"] = True

    return out


def _condition_depends_on(cond: dict) -> List[str]:
    """Get the names of parameters that this condition depends on.

    Args:
        cond (dict): condition

    Returns:
        List[str]: names of parameters
    """
    if isinstance(cond, bool):
        # if this is a boolean condition, return an empty list
        return []
    elif isinstance(cond, dict):
        # we only support equals statements for now
        assert len(cond) == 1
        assert list(cond.keys()) == ["equals"]
        assert isinstance(cond["equals"], dict)
        assert len(cond["equals"]) == 1
        return list(cond["equals"].keys())
    else:
        raise RuntimeError(f"Unknown condition: {cond}")


def _eval_condition(cond: bool | dict, param_set: dict[str, Any]) -> bool:
    """Check if an `if` condition is satisfied.

    Args:
        cond (bool | dict): if condition
        param_set (dict): parameter set

    Returns:
        bool: if the spec matches the set
    """
    if isinstance(cond, bool):
        # if this is a boolean condition, return it
        return cond
    elif isinstance(cond, dict):
        # we only support equals statements for now
        assert list(cond.keys()) == ["equals"]
        assert isinstance(cond["equals"], dict)
        assert len(cond["equals"]) == 1
        cond_name, cond_value = list(cond["equals"].items())[0]

        return cond_name in param_set and param_set[cond_name] == cond_value
