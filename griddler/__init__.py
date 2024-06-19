import random
import polars as pl
from typing import Callable, Any

class ParameterSet(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate()

    def hash(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        keys = sorted(self.keys())
        values = [self[key] for key in keys]
        return tuple((key, value) for key, value in zip(keys, values))

    def validate(self):
        for key in self.keys():
            if not isinstance(key, str):
                raise ValueError(f"parameter set key {key} is not a string")

        for value in self.values():
            self.validate_value(value)

    @classmethod
    def validate_value(cls, value):
        if isinstance(value, (str, int, float)):
            return True
        elif isinstance(value, tuple):
            for x in value:
                cls.validate_value(x)
        else:
            raise ValueError(f"parameter value {value} is of invalid type {type(value)}")


def run_squash(func: Callable[..., pl.DataFrame], parameter_sets):
    return pl.concat(
        [
            func(ps).with_columns(
                [pl.lit(value).alias(key) for key, value in ps.items()]
            )
            for ps in parameter_sets
        ],
        how="vertical",
    )


def replicated(
    func,
    n_replicates_key="n_replicates",
    seed_key="seed",
    replicate_var="replicate",
    replicate_type=pl.Int64,
):
    def replicated_func(parameter_set, *args, **kwargs):
        assert isinstance(parameter_set, dict)
        assert n_replicates_key in parameter_set
        assert seed_key in parameter_set

        # remove replicate-related keywords
        norep_parameter_set = {
            key: value
            for key, value in parameter_set.items()
            if key not in [n_replicates_key, seed_key]
        }

        random.seed(parameter_set[seed_key])

        return pl.concat(
            [
                (
                    func(norep_parameter_set, *args, **kwargs).with_columns(
                        pl.lit(i, dtype=replicate_type).alias(replicate_var)
                    )
                )
                for i in range(parameter_set[n_replicates_key])
            ]
        )

    return replicated_func
