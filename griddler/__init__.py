import hashlib
import json
import random
from typing import Any, Callable, Optional, Sequence

import polars as pl
import progressbar


class ParameterSet(dict):
    """A simple extension of the `dict` class, requiring that:

    1. all keys are strings, and
    2. all values are valid. Valid values are integers, floats, or strings, or
      lists (or tuples) composed of valid values.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate()

    def stable_hash(self, hash_length: int = 10) -> str:
        """Create a stable hash of this parameter set. Implemented as a BLAKE2
        digest of the JSON representation of the parameter set:

        Examples:
            >>> ParameterSet({"gamma": 1.0, "R0": 0.9}).stable_hash()
            '544601bc1dbb3346faff' # pragma: allowlist secret

        Args:
            hash_length: Number of characters in the hash

        Returns:
            hash
        """
        data = json.dumps(self, sort_keys=True)
        return hashlib.blake2b(data.encode(), digest_size=hash_length).hexdigest()

    def validate(self):
        for key in self.keys():
            if not isinstance(key, str):
                raise ValueError(f"parameter set key {key!r} is not a string")

        for value in self.values():
            self.validate_value(value)

    @classmethod
    def validate_value(cls, value):
        if isinstance(value, (str, int, float)):
            return True
        elif isinstance(value, (list, tuple)):
            for x in value:
                cls.validate_value(x)
        elif isinstance(value, dict):
            assert all(isinstance(k, str) for k in value.keys())
            for x in value.values():
                cls.validate_value(x)
        else:
            raise ValueError(
                f"parameter value {value!r} is of invalid type {type(value)}"
            )


def run_squash(
    func: Callable[..., pl.DataFrame],
    parameter_sets: Sequence[dict],
    add_parameters: bool = True,
    parameter_columns: Optional[Sequence[str]] = None,
    add_hash: bool = True,
    hash_column: str = "hash",
    progress: bool = True,
):
    # run all parameter sets, optionally wrapping in a progress bar
    parameter_sets_run = (
        progressbar.progressbar(parameter_sets) if progress else parameter_sets
    )
    outputs = [func(ps) for ps in parameter_sets_run]

    output_vars = set([column for output in outputs for column in output.columns])

    # the hash column name shouldn't collide with any output or parameter columns
    if add_hash:
        assert hash_column not in output_vars

    if add_parameters:
        # if parameter_vars is not specified, then include all parameters
        if parameter_columns is None:
            parameter_columns = list(
                set([key for ps in parameter_sets for key in ps.keys()])
            )

        # there should be no names in common between the output columns and the parameters we want
        # to add
        assert len(output_vars & set(parameter_columns)) == 0

        # there should be no collision with hash column
        if add_hash:
            assert hash_column not in parameter_columns

        # add parameter columns
        outputs = [
            output.with_columns(
                [_as_expr(ps[key]).alias(key) for key in parameter_columns]
            )
            for output, ps in zip(outputs, parameter_sets)
        ]

    # add hash column
    if add_hash:
        hashes = [ParameterSet(ps).stable_hash() for ps in parameter_sets]
        outputs = [
            output.with_columns(pl.lit(hash).alias(hash_column))
            for output, hash in zip(outputs, hashes)
        ]

    return pl.concat(outputs, how="vertical")


def _as_expr(x: Any) -> pl.Expr:
    """Cast object as polars-compatible value

    Args:
        x: Input value

    Returns:
        pl.Expr: If `x` is a dict, a `pl.struct()`. Otherwise, a `pl.lit()`.
    """
    if isinstance(x, dict):
        return pl.struct([_as_expr(value).alias(key) for key, value in x.items()])
    elif isinstance(x, (str, int, float, list, tuple)):
        return pl.lit(x)
    else:
        raise RuntimeError(f"Parameter value {x} of invalid type {type(x)}")


def replicated(
    func: Callable[..., pl.DataFrame],
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

        # run the function
        random.seed(parameter_set[seed_key])

        outputs = [
            func(norep_parameter_set, *args, **kwargs)
            for i in range(parameter_set[n_replicates_key])
        ]

        return pl.concat(
            [
                output.with_columns(
                    pl.lit(i, dtype=replicate_type).alias(replicate_var)
                )
                for i, output in enumerate(outputs)
            ]
        )

    return replicated_func
