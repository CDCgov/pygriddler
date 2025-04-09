import functools
import importlib.resources
import json
from typing import Any, Iterable, List

import jsonschema


class Spec(dict):
    """
    A parameter specification, or Spec, is an extension of a dictionary,
    with the added requirement that all keys be strings.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self:
            assert isinstance(key, str)

    def deparse(self) -> dict:
        return dict(self)


class Experiment:
    """
    An Experiment is set of Specs, supporting union (concatenation)
    and Cartesian products.
    """

    def __init__(self, specs: Iterable[Spec]):
        self.specs = list(specs)

        for spec in self.specs:
            assert isinstance(spec, Spec)

    def __or__(self, other: "Experiment") -> "Experiment":
        assert isinstance(other, Experiment)
        return Experiment(self.specs + other.specs)

    def __mul__(self, other: "Experiment") -> "Experiment":
        assert isinstance(other, Experiment)

        # every pair of specs should have disjoint keys
        for x in self.specs:
            for y in other.specs:
                shared_keys = set(x.keys()).intersection(y.keys())
                if len(shared_keys) > 0:
                    raise RuntimeError(
                        f"Keys are not disjoint in Experiment product: {shared_keys}"
                    )

        return Experiment([Spec(x | y) for x in self.specs for y in other.specs])

    @staticmethod
    def parse(x: list[dict[str, Any]] | dict[str, Any]) -> "Experiment":
        if isinstance(x, list):
            return Experiment([Spec(elt) for elt in x])
        elif isinstance(x, dict):
            assert len(x) == 1
            key, value = list(x.items())[0]
            assert isinstance(value, list)
            subexperiments = [Experiment.parse(elt) for elt in value]
            if key == "union":
                return functools.reduce(lambda x, y: x | y, subexperiments)
            elif key == "product":
                return functools.reduce(lambda x, y: x * y, subexperiments)
            else:
                raise RuntimeError(f"Unknown experiment key: {key}")
        else:
            raise RuntimeError(f"Unknown experiment type: {x} of type {type(x)}")

    def deparse(self) -> List[dict[str, Any]]:
        """Convert this Experiment into a list of dictionaries.

        Returns:
            Iterable[dict[str, Any]]: list of dictionaries
        """
        return [spec.deparse() for spec in self.specs]


class Griddle:
    def __init__(self, griddle: dict):
        """Create a parameter griddle

        Args:
            griddle (dict): griddle specification
        """
        self.griddle = griddle

        # do syntactic validation
        jsonschema.validate(instance=self.griddle, schema=self.load_schema())
        # check for version
        assert self.griddle["version"] == "v0.3", "Only v0.3 griddles are supported"

    def parse(self) -> List[dict[str, Any]]:
        """Convert this griddle into a list of parameter sets.

        Returns:
            List[dict]: list of parameter sets
        """
        # extract the parameters section of the griddle
        experiment = self.griddle["experiment"]
        return Experiment.parse(experiment).deparse()

    @staticmethod
    def load_schema() -> dict:
        """Load the griddle schema from the package directory.

        Returns:
            dict: schema
        """
        with importlib.resources.open_text("griddler", "schema.json") as f:
            schema = json.load(f)

        return schema
