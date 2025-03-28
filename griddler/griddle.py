import importlib.resources
import json
import uuid
from typing import Any, Iterable, List, Set

import jsonschema
import networkx as nx
import yaml


class Param:
    name: str
    if_: bool | dict

    @classmethod
    def from_json(cls, name: str, spec: dict[str, Any]) -> "Param":
        if "fix" in spec:
            return FixParam(name=name, value=spec["fix"], if_=spec.get("if", True))
        elif "vary" in spec and isinstance(spec["vary"], dict):
            return Bundle(
                name=name,
                parameter_names=list(spec["vary"].keys()),
                values=list(spec["vary"].values()),
                if_=spec.get("if", True),
            )
        elif "vary" in spec and isinstance(spec["vary"], list):
            bundle_name = f"bundle-{name}-{uuid.uuid4()}"
            return Bundle(
                # generate an ad hoc bundle name
                name=bundle_name,
                # put the parameter name inside the bundle
                parameter_names=[name],
                values=[spec["vary"]],
                if_=spec.get("if", True),
            )
        else:
            raise RuntimeError(f"Unknown parameter specification: {name}: {spec}")

    def depends_on(self) -> Set[str]:
        """Get the names of parameters that this parameter depends on.

        Returns:
            List[str]: names of parameters
        """
        if isinstance(self.if_, bool):
            # if this is a boolean condition, return an empty list
            return set()
        elif isinstance(self.if_, dict):
            # we only support equals statements for now
            assert len(self.if_) == 1
            assert list(self.if_.keys()) == ["equals"]
            assert isinstance(self.if_["equals"], dict)
            assert len(self.if_["equals"]) == 1
            return set(self.if_["equals"].keys())
        else:
            raise RuntimeError(f"Unknown condition: {self.if_}")

    def eval_condition(self, param_set: dict[str, Any]) -> bool:
        """Check if an `if` condition is satisfied.

        Args:
            param_set (dict): parameter set

        Returns:
            bool: if the spec matches the set
        """
        if isinstance(self.if_, bool):
            # if this is a boolean condition, return it
            return self.if_
        elif isinstance(self.if_, dict):
            # we only support equals statements for now
            assert list(self.if_.keys()) == ["equals"]
            assert isinstance(self.if_["equals"], dict)
            assert len(self.if_["equals"]) == 1
            cond_name, cond_value = list(self.if_["equals"].items())[0]

            return cond_name in param_set and param_set[cond_name] == cond_value
        else:
            raise RuntimeError(f"Unknown condition: {self.if_}")

    def augment_parameter_set(
        self, parameter_set: dict[str, Any]
    ) -> Iterable[dict[str, Any]]:
        """Add this parameter to a parameter set, potentially producing multiple
        output parameter sets

        Args:
            param_set (dict): input parameter set

        Returns:
            Iterable[dict[str, Any]]: one or more output updated parameter sets
        """
        raise NotImplementedError


class FixParam(Param):
    def __init__(self, name: str, value: Any, if_: bool | dict):
        self.name = name
        self.value = value
        self.if_ = if_

    def augment_parameter_set(
        self, parameter_set: dict[str, Any]
    ) -> Iterable[dict[str, Any]]:
        # just add this fixed value
        assert self.name not in parameter_set
        parameter_set[self.name] = self.value
        return [parameter_set]


class Bundle(Param):
    def __init__(
        self,
        name: str,
        parameter_names: List[str],
        values: List[List],
        if_: bool | dict,
    ):
        self.name = name
        self.parameter_names = parameter_names
        self.values = values
        self.if_ = if_

        # check that all values have the same length
        n = [len(v) for v in values]
        assert len(set(n)) == 1, (
            f"Varying parameters in bundle {name} must have the same number of values"
        )
        self.n = n[0]

    def augment_parameter_set(
        self, parameter_set: dict[str, Any]
    ) -> Iterable[dict[str, Any]]:
        out = [parameter_set.copy() for _ in range(self.n)]
        for i in range(self.n):
            for name, value in zip(self.parameter_names, self.values):
                out[i][name] = value[i]

        return out


class Griddle:
    def __init__(self, griddle: dict):
        self.griddle = griddle

        # do syntactic validation
        jsonschema.validate(instance=self.griddle, schema=self.load_schema())
        # check for version
        assert self.griddle["version"] == "v0.3", "Only v0.3 griddles are supported"

    def parse(self) -> List[dict]:
        """Convert a griddle into a list of parameter sets.

        Args:
            griddle (dict): griddle

        Returns:
            List[dict]: list of parameter sets
        """
        # extract the parameters section of the griddle
        params = self.griddle["parameters"]
        assert isinstance(params, dict)

        return self._parse_params(params)

    @classmethod
    def _parse_params(cls, params_dict: dict[str, Any]) -> List[dict]:
        """Parse the parameters section of the griddle"""
        # parse the parameters into objects
        params = [Param.from_json(name, spec) for name, spec in params_dict.items()]

        # check that no parameter names are repeated
        cls._validate_parameter_names(params)

        # determine the order in which we'll add parameters to the parameter sets
        param_order = cls._get_param_order(params)

        # initialize the output parameter sets
        parameter_sets = [{}]

        # go through the params in order
        for param in sorted(params, key=lambda x: param_order.index(x.name)):
            # each time, iterate over all the parameter sets, augmenting them
            # to create a new list of parameter sets
            new_parameter_sets = []

            for ps in parameter_sets:
                # check if the `if` condition is satisfied
                if param.eval_condition(ps):
                    # get the updated (& potentially multiplied) parameter sets
                    augmented_sets = param.augment_parameter_set(ps)
                    # add the new parameter sets to the list
                    new_parameter_sets.extend(augmented_sets)
                else:
                    # if the condition isn't satisfied, just add the old
                    # parameter set to the list
                    new_parameter_sets.append(ps)

            parameter_sets = new_parameter_sets

        return parameter_sets

    @classmethod
    def _get_param_order(cls, params: Iterable[Param]) -> List[str]:
        """Get the order of parameters in the griddle, using the DAG of `if`s.

        Args:
            params (List[Param]): list of parameter objects

        Returns:
            List[str]: order of parameters (by name)
        """
        # make a mapping from parameter name to parameter/bundle name/ID
        name_map = {}

        for param in params:
            if isinstance(param, FixParam):
                # for fixed params, there is no ambiguity
                name_map[param.name] = param.name
            elif isinstance(param, Bundle):
                # for bundles, point from the parameter names in the bundle to
                # the bundle ID
                for name in param.parameter_names:
                    name_map[name] = param.name
            else:
                raise RuntimeError(f"Unknown parameter type: {type(param)}")

        # create a directed graph from the `if`s
        # nodes are the parameters/bundles
        G = nx.DiGraph()
        for param in params:
            G.add_node(param.name)

            # if this parameter depends on other ones, add edges from
            # those parameters to this one
            for cond_param_name in param.depends_on():
                # get the parameter name from the name map
                cond_obj_name = name_map[cond_param_name]
                G.add_edge(cond_obj_name, param.name)

        # confirm this graph is a DAG
        if not nx.is_directed_acyclic_graph(G):
            raise RuntimeError("The `if` conditions form a cycle.")

        # get the topological sort of the graph
        return list(nx.topological_sort(G))

    @classmethod
    def _validate_parameter_names(cls, params: Iterable[Param]) -> None:
        """Check that there are no name collisions, especially with the varying
        bundles.

        Args:
            params (List[Param]): list of parameter objects
        """
        names = []
        for param in params:
            if isinstance(param, FixParam):
                assert param.name not in names, (
                    f"Duplicate parameter name: {param.name}"
                )
                names.append(param.name)
            elif isinstance(param, Bundle):
                for name in param.parameter_names:
                    assert name not in names, f"Duplicate parameter name: {name}"
                    names.append(name)
            else:
                raise RuntimeError(f"Unknown parameter type: {type(param)}")

    @staticmethod
    def load_schema() -> dict:
        with importlib.resources.open_text("griddler", "schema.json") as f:
            schema = json.load(f)

        return schema

    @staticmethod
    def from_yaml(path: str) -> "Griddle":
        with open(path) as f:
            griddle = yaml.safe_load(f)

        return Griddle(griddle)

    @staticmethod
    def from_json(path: str) -> "Griddle":
        with open(path) as f:
            griddle = json.load(f)

        return Griddle(griddle)
