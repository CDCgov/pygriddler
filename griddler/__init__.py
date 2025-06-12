from typing import Any, Iterable, List

import griddler.schemas.v03


class Spec(dict):
    """
    A parameter specification, or Spec, is an extension of a dictionary,
    with the added requirement that all keys be strings.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self:
            assert isinstance(key, str)

    def to_dict(self) -> dict:
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

    def to_dicts(self) -> List[dict[str, Any]]:
        """Convert this Experiment into a list of dictionaries.

        Returns:
            Iterable[dict[str, Any]]: list of dictionaries
        """
        return [spec.to_dict() for spec in self.specs]


def parse(griddle: dict) -> Experiment:
    assert isinstance(griddle, dict), "Griddle must be a dictionary"
    assert "schema" in griddle, "Griddle must have a schema"

    match griddle["schema"]:
        case "v0.3":
            return griddler.schemas.v03.parse(griddle)
        case _:
            raise RuntimeError(f"Unknown griddle schema: {griddle['schema']}")
