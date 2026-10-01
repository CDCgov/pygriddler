import abc
import functools
import itertools
from collections.abc import Iterable, Iterator


class Experiment(abc.ABC):
    """An Experiment can iterate over its constituent Specs.

    It also supports union and product operations.
    """

    def __init__(self, specs: Iterable[dict]):
        self.specs = list(specs)

        for spec in self:
            assert isinstance(spec, dict)

    def union(self, other: "Experiment") -> "Experiment":
        """Union of two experiments."""
        assert isinstance(other, Experiment)
        return ExperimentUnion([self, other])

    def __or__(self, other: "Experiment") -> "Experiment":
        return self.union(other)

    def __mul__(self, other: "Experiment") -> "Experiment":
        """Cartesian product of two experiments."""
        assert isinstance(other, Experiment)
        return ExperimentProduct([self, other])

    def __str__(self) -> str:
        spec_str = ", ".join(str(spec) for spec in self)
        return f"Experiment([{spec_str}])"

    def __iter__(self) -> Iterator[dict]:
        yield from self.specs


class ExperimentUnion(Experiment):
    """A union of constituent Experiments.

    It iterates over its Specs by iterating over its Experiments and
    each of their Specs.
    """

    def __init__(self, experiments: Iterable[Experiment]):
        self.experiments = experiments

    def __str__(self) -> str:
        ex_string = ", ".join(str(ex) for ex in self.experiments)
        return f"ExperimentUnion([{ex_string}])"

    def __iter__(self) -> Iterator[dict]:
        for exp in self.experiments:
            yield from exp


class ExperimentProduct(Experiment):
    """A Cartesian product of constituent Experiments.

    It iterates over its Specs by iterating over combinations of its
    constituent Experiments, iterating over the Specs from those
    experiments, and taking the union of those Specs.
    """

    def __init__(self, experiments: Iterable[Experiment]):
        self.experiments = experiments

    def __str__(self) -> str:
        ex_string = ", ".join(str(ex) for ex in self.experiments)
        return f"ExperimentProduct([{ex_string}])"

    def __iter__(self) -> Iterator[dict]:
        for combination in itertools.product(*self.experiments):
            yield functools.reduce(lambda acc, x: acc | x, combination, {})
