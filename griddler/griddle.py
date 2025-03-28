import importlib.resources
import itertools
import json
from typing import List

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

    # check that no parameter names are repeated
    _validate_parameter_names(params)

    # convert all the short-form varying bundles into canonical form
    params = {name: _to_canonical_form(name, spec) for name, spec in params.items()}

    # determine the order in which we'll add parameters to the parameter sets
    param_order = _get_param_order(params)

    # initialize the output parameter sets
    parameter_sets = [{}]

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
        if "if" in spec:
            for cond_name in spec["if"].keys():
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


def _to_canonical_form(name: str, spec: dict) -> dict:
    """Convert a parameter specification into canonical form.

    Args:
        name (str): parameter (or bundle) name
        spec (dict): parameter specification

    Returns:
        dict: canonical form
    """
    # if this is a short-form bundle, convert it to canonical form
    if "vary" in spec and isinstance(spec["vary"], list):
        return {spec["name"]: {"vary": {spec["name"]: spec["vary"]}}}

    # otherwise, just return the original spec
    return spec
