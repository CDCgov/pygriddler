# griddler

## Parameter sets

The `ParameterSet` class is an extension of `dict` that provides some extra functionality.

It ensures that all keys are strings and all values are valid. A value is valid if it is a float, integer, or string, or if it is a list or tuple composed of other valid values.

A parameter set has a stable hash, implemented as a BLAKE2 digest of the JSON representation of the parameter set:
```python
>>> ParameterSet({"gamma": 1.0, "beta": 2.0}).stable_hash()
'2d220d93aff966ac7c50' # pragma: allowlist secret
```

## Parsing griddles

At the command line, `griddler parse < griddle.yaml > parameter_sets.yaml` will read a "griddle" yaml and output a list of lists yaml.

In a script, the same could be accomplished with:
```python
parameter_sets = griddler.griddle.read("griddle.yaml")

with open("parameter_sets.yaml", "w") as f:
    yaml.dump(parameter_sets, f)
```

## Running a function and "squashing" results

Given

- a function, say `simulate()`, that takes a parameter set and returns a [polars DataFrame](https://docs.pola.rs/py-polars/html/reference/dataframe/index.html), and
- a list of parameter sets, such as from `griddler.griddle.read()`,

then `griddle.run_squash(simulate, parameter_sets)` will return a "squashed" version of the results. This is a single DataFrame consisting of the other DataFrames, vertically concatenated.

If `add_parameters=True` and `parameter_columns=None` (which is the default), then each resulting DataFrame has all the input parameters. This will only work if all the parameters have scalar values that can be coerced with [`pl.lit()`](https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.lit.html). A subset of parameters can be added using `parameter_columns`.

If `add_hash=True` (which is the default), then a column (with name equal to `hash_column`, which is `"hash"` by default) with the parameter set hash will also be added.

## Running a function with replicates

Given

- a function, say `simulate()`, like in the example above, and
- a list of parameter sets, as above, but with each parameter set having keys `"n_replicates"` and `"seed"`,

then `replicated(simulate)` is itself a function, with the same signature as `simulate()`. It removes the `"n_replicates"` and `"seeds"` parameters from each parameter set, sets the seed with [`random.seed()`](https://docs.python.org/3/library/random.html#random.seed), and then runs `simulate()` on the remaining parameters `n_replicate` times. The results gets squashed with a column `"replicate"` (or whatever name you specify).
