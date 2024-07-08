# griddler

This package is an opinionated tool for managing inputs to simulations or other analytical functions.

## Functionality

### Parameter sets

A *parameter set* is a mapping of parameter names to parameter values. In `griddler`, the `ParameterSet` class is an extension of `dict` that provides some extra functionality.

It ensures that all keys are strings and all values are valid. A value is valid if it is a float, integer, or string, or if it is a list or tuple composed of other valid values (e.g., a list of integers).

A parameter set has a stable hash, implemented as a BLAKE2 digest of the JSON representation of the parameter set:
```python
>>> ParameterSet({"gamma": 1.0, "beta": 2.0}).stable_hash()
'2d220d93aff966ac7c50' # pragma: allowlist secret
```

### Griddles

A *griddle* is an intuitive file format for specifying lists of parameter sets. The syntax is inspired by the ["matrix" strategy](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstrategymatrix) in GitHub Workflow files.

The griddle format assumes that parameters come in three flavors:

- Baseline: You want these parameters in common across most iterations of your simulation.
- Grid: You want to perform a Cartesian product over lists of values for some parameters.
- Nested: For certain combinations of "gridded" parameters, you want to specify additional parameters, potentially overwriting the baseline parameters.

The griddle format is easy to read and write. A complete specification of the format, along with examples are below.

### Parsing griddles

At the command line, `griddler parse < griddle.yaml > parameter_sets.yaml` will read a griddle and output a YAML file. This output file is a list of named lists. Each named list is a parameter set, one for each element of the grid.

In a script, the same could be accomplished with:
```python
parameter_sets = griddler.griddle.read("griddle.yaml")

with open("parameter_sets.yaml", "w") as f:
    yaml.dump(parameter_sets, f)
```

### Running a function and "squashing" results

Given

- a function, say `simulate()`, that takes a parameter set and returns a [polars DataFrame](https://docs.pola.rs/py-polars/html/reference/dataframe/index.html), and
- a list of parameter sets, such as from `griddler.griddle.read()`,

then `griddle.run_squash(simulate, parameter_sets)` will return a "squashed" version of the results. This is a single DataFrame consisting of the other DataFrames, vertically concatenated.

If `add_parameters=True` and `parameter_columns=None` (which is the default), then each resulting DataFrame has all the input parameters. This will only work if all the parameters have scalar values that can be coerced with [`pl.lit()`](https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.lit.html). A subset of parameters can be added using `parameter_columns`.

If `add_hash=True` (which is the default), then a column (with name equal to `hash_column`, which is `"hash"` by default) with the parameter set hash will also be added.

### Running a function with replicates

Given

- a function, say `simulate()`, like in the example above, and
- a list of parameter sets, as above, but with each parameter set having keys `"n_replicates"` and `"seed"`,

then `replicated(simulate)` is itself a function, with the same signature as `simulate()`. It removes the `"n_replicates"` and `"seeds"` parameters from each parameter set, sets the seed with [`random.seed()`](https://docs.python.org/3/library/random.html#random.seed), and then runs `simulate()` on the remaining parameters `n_replicate` times. The results gets squashed with a column `"replicate"` (or whatever name you specify).

## The griddle format

### Specification

- A griddle is YAML file, specifying a top-level dictionary.
  - The top-level dictionary have at least one of `baseline_parameters` or `grid_parameters` as a key.
  - If the top-level dictionary has `grid_parameters`, it may also have `nested_parameters` as a key.
  - It must not have any other keys.
- `baseline_parameters` is a dictionary.
  - The keys are parameter names; the values are parameter values.
  - A parameter value is valid if it is an integer, float, or string, or if it a string made up of valid values.
- `grid_parameters` is a dictionary.
  - The keys are parameter names. Each value is a list. The elements in that list are the parameter values gridded over.
  - No keys can be repeated between `baseline_parameters` and `grid_parameters`.
- `nested_parameters` is a list (not a dictionary).
  - Each element is a dictionary, called a "nest."
  - Every nest have at least one key that appears in the grid.
  - Key in each nest must be either:
     1. present in `grid_parameters` or `baseline_parameters` (but not both), *or*
     1. present in each nest.

When parsed, the griddle expands into a list of dictionaries, each of which is a parameter set.

### Examples

In the simplest case, the griddle will produce one parameter set:

```yaml
baseline_parameters:
  R0: 3.0
  infectious_period: 1.0
  p_infected_initial: 0.001
```

But maybe you want to run simulations over a grid of parameters. So instead use
`grid_parameters`:

```yaml
baseline_parameters:
  p_infected_initial: 0.001

grid_parameters:
  R0: [2.0, 3.0]
  infectious_period: [0.5, 2.0]
```

This will run 4 parameter sets, over the Cartesian product of the parameter values
for $R_0$ and $1/\gamma$.

If you want to run many replicates of each of those parameter sets, specify `seed` and `n_replicates`:

```yaml
baseline_parameters:
  p_infected_initial: 0.001
  seed: 42
  n_replicates: 100

grid_parameters:
  R0: [2.0, 3.0]
  infectious_period: [0.5, 2.0]
```

This will still produce 4 parameter sets. It will be up to your wrapped simulation function to know how to run all the replicates. The `replicated()` function in this package is designed for that.

If you want to include nested values, use `nested_parameters`. The keys in each nest that match `grid_parameters` will be used to determine which part of the grid we are in, and the rest of the parameters in the nest will be added in to that part of the grid. For example:

```yaml
grid_parameters:
  R0: [2.0, 4.0]
  infectious_period: [0.5, 2.0]

nested_parameters:
  - R0: 2.0
    p_infected_initial: 0.01
  - R0: 4.0
    p_infected_initial: 0.0001
```

The nested values of $R_0$ match against the grid, and will add the $p_{I0}$ values in to those parts of the grid. Thus, this will produce 4 parameter sets:

1. $R_0=2$, $1/\gamma=0.5$, $p_{I0}=10^{-2}$
1. $R_0=2$, $1/\gamma=2$, $p_{I0}=10^{-2}$
1. $R_0=4$, $1/\gamma=0.5$, $p_{I0}=10^{-4}$
1. $R_0=4$, $1/\gamma=2$, $p_{I0}=10^{-4}$

Nested parameters can be used to make named scenarios:

```yaml
baseline_parameters:
  p_infected_initial: 0.001

grid_parameters:
  scenario: [pessimistic, optimistic]

nested_parameters:
  - scenario: pessimistic
    R0: 4.0
    infectious_period: 2.0
  - scenario: optimistic
    R0: 2.0
    infectious_period: 0.5
```

This will produce 2 parameter sets.

You cannot repeat a parameter name that is in `baseline_parameters` in `grid_parameters`, because it would be overwritten every time. But you can use `nested_parameters` to *sometimes* overwrite a baseline parameter value:

```yaml
baseline_parameters:
  R0: 2.0
  infectious_period: 1.0
  p_infected_initial: 0.001

grid_parameters:
  scenario: [short_infection, long_infection, no_infection]
  population_size: [!!float 1e3, !!float 1e4]

nested_parameters:
  - scenario: short_infection
    infectious_period: 0.5
  - scenario: long_infection
    infectious_period: 2.0
  - scenario: no_infection
    R0: 0.0
```

This will produce 6 parameter sets:

1. $R_0 = 2$, $\gamma = 1/0.5$, $N = 10^3$, $p_{I0} = 10^{-3}$
1. $R_0 = 2$, $\gamma = 1/0.5$, $N = 10^4$, $p_{I0} = 10^{-3}$
1. $R_0 = 2$, $\gamma = 1/2.0$, $N = 10^3$, $p_{I0} = 10^{-3}$
1. $R_0 = 2$, $\gamma = 1/2.0$, $N = 10^4$, $p_{I0} = 10^{-3}$
1. $R_0 = 0$, $\gamma = 1.0$, $N = 10^3$, $p_{I0} = 10^{-3}$
1. $R_0 = 0$, $\gamma = 1.0$, $N = 10^4$, $p_{I0} = 10^{-3}$

All of them have the same fixed parameter value $p_{I0}$. Half of them have each of the two grid parameter values $N$. For each of the three scenarios, there is a mix of $R_0$ and $\gamma$ values drawn from `baseline_parameters` and `nested_parameters`.

## Project Admin

Scott Olesen <ulp7@cdc.gov> (CDC/IOD/ORR/CFA)

---

## General Disclaimer

This repository was created for use by CDC programs to collaborate on public
health related projects in support of the
[CDC mission](https://www.cdc.gov/about/organization/mission.htm). GitHub is not
hosted by the CDC, but is a third party website used by CDC and its partners to
share information and collaborate on software. CDC use of GitHub does not imply
an endorsement of any one particular service, product, or enterprise.

## Public Domain Standard Notice

This repository constitutes a work of the United States Government and is not
subject to domestic copyright protection under 17 USC § 105. This repository is
in the public domain within the United States, and copyright and related rights
in the work worldwide are waived through the
[CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
All contributions to this repository will be released under the CC0 dedication.
By submitting a pull request you are agreeing to comply with this waiver of
copyright interest.

## License Standard Notice

This repository is licensed under ASL v2 or later.

This source code in this repository is free: you can redistribute it and/or
modify it under the terms of the Apache Software License version 2, or (at your
option) any later version.

This source code in this repository is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Apache Software
License for more details.

You should have received a copy of the Apache Software License along with this
program. If not, see http://www.apache.org/licenses/LICENSE-2.0.html

The source code forked from other open source projects will inherit its license.

## Privacy Standard Notice

This repository contains only non-sensitive, publicly available data and
information. All material and community participation is covered by the
[Disclaimer](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md) and
[Code of Conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).
For more information about CDC's privacy policy, please visit
[http://www.cdc.gov/other/privacy.html](https://www.cdc.gov/other/privacy.html).

## Contributing Standard Notice

Anyone is encouraged to contribute to the repository by
[forking](https://help.github.com/articles/fork-a-repo) and submitting a pull
request. (If you are new to GitHub, you might start with a
[basic tutorial](https://help.github.com/articles/set-up-git).) By contributing
to this project, you grant a world-wide, royalty-free, perpetual, irrevocable,
non-exclusive, transferable license to all users under the terms of the
[Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or
later.

All comments, messages, pull requests, and other submissions received through
CDC including this GitHub page may be subject to applicable federal law,
including but not limited to the Federal Records Act, and may be archived. Learn
more at
[http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

## Records Management Standard Notice

This repository is not a source of government records but is a copy to increase
collaboration and collaborative potential. All government records will be
published through the [CDC web site](http://www.cdc.gov).
