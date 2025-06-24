from typing import Iterable


class Experiment:
    """
    An Experiment is set of Specs, supporting union and product operations.
    """

    def __init__(self, specs: Iterable[dict]):
        self.specs = list(specs)

        for spec in self.specs:
            assert isinstance(spec, dict)

    def __str__(self) -> str:
        spec_str = ", ".join(str(spec) for spec in self.specs)
        return f"Experiment([{spec_str}])"

    def union(self, other: "Experiment") -> "Experiment":
        assert isinstance(other, Experiment)
        return Experiment(self.specs + other.specs)

    def __or__(self, other: "Experiment") -> "Experiment":
        return self.union(other)

    def __mul__(self, other: "Experiment") -> "Experiment":
        assert isinstance(other, Experiment)

        return Experiment([x | y for x in self.specs for y in other.specs])

    def __iter__(self) -> Iterable[dict]:
        return iter(self.specs)
