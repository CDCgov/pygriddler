# The griddle schema

Griddler is a tool for parsing a *griddle* to produce an array of *parameter sets*.

A *parameter* consists of a string *name* and a *value* of arbitrary type. A *parameter set* is an object whose keywords are the parameter names and whose values are the corresponding parameter values.

!!! note

    This document uses JSON typing nomenclature. A JSON array is like a Python list. A JSON object is a Python dictionary. An object keyword is like a dictionary key.


A *griddle* is an object with two keywords: `version` and `parameters`. `version` specifies the version of the griddler schema, currently `"v0.3"`. `parameters` is an array of parameter *specifications*. Each specification specifies one of:

1. a *fixed* parameter that appears in every parameter set (so long as it is not *conditioned*) with the same value,
2. a single *varying* parameter that takes on different values in different parameters sets, or
3. a *bundle* of parameters that vary together.

In typical practice, griddles are read in from YAML or JSON files, and parameter sets are serialized as JSON files. That convention is used in the examples here.

## Minimal griddle

The minimal functional griddle has a version and no dimensions.

```yaml
version: v0.3
dimensions: {}
```

## Fixed parameters

The canonical form is:

```yaml
version: v0.3
dimensions:
  - name: NAME
    type: fix
    value: VALUE
```

In this and future examples, capitals are used to designate values that would be filled in. In future examples, `version` is omitted for brevity.

Griddler supports a short form for fixed parameters, so long as parameter name is not a reserved keyword (`name`, `type`, `vary`, `value`, `values`, `if`, `comment`):

```yaml
parameters:
  - NAME: VALUE
```

Note that the value of a fixed parameter need not be a scalar. For example, `delay_distribution_pmf` would appear as the same array in all the parameter sets:

```yaml
parameters:
  - delay_distribution_pmf: [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0]
```

## Varying parameters

The canonical form is:

```yaml
parameters:
  - type: vary
    values:
    - name: NAME1
      values: [NAME1_VALUE1, NAME1_VALUE2] # and so on for NAME1_VALUE3, etc.
    - name: NAME2
      values: [NAME2_VALUE1, NAME2_VALUE2]
    # and so on for NAME3, etc.
```

In the parameter sets, the `*_VALUE1` values will always appear together, the `*_VALUE2` will always appear together, and so forth. All the `values` must be of equal length.

Griddler support a short form, which assumes that the parameter names are not reserved keywords:

```yaml
parameters:
  - type: vary
    values:
      NAME1: [NAME1_VALUE1, NAME1_VALUE2]
      NAME2: [NAME2_VALUE1, NAME2_VALUE2]
```

For a grid dimension that has only one parameter, whose name is not a reserved word, griddler supports an additional short form:

```yaml
parameters:
  - NAME: {vary: [VALUE1, VALUE2]} # and so on for VALUE3, etc.
```

### Conditioned parameters

A conditioned parameter will only be present in an parameter set when some one or more other parameters are present and have some particular values.

```yaml
parameters:
  # conditioned fixed parameter, canonical form
  - name: NAME
    if: {COND_NAME1: COND_VALUE1, COND_NAME2: COND_VALUE2}
    type: fix
    value: VALUE

  # (there is no short form for conditioned fixed parameter)

  # conditioned varying parameter, canonical form
  - type: vary
    if: {COND_NAME1: COND_VALUE1, COND_NAME2: COND_VALUE2}
    values:
      - name: NAME
        values: [VALUE1, VALUE2]

  # conditioned varying parameter, short form
  - type: vary
    if: {COND_NAME1: COND_VALUE1, COND_NAME2: COND_VALUE2}
    values:
      NAME: [VALUE1, VALUE2]

  # (there is no short form for one-parameter grid dimension short form)
```

## Comments

Any content in a `comment` field is ignored. This is not important in YAML files, which have native comments, but can be useful in a human-written JSON. Comments are only available in canonical forms.

```yaml
parameters:
  - name: FIXED_NAME
    comment: THIS TEXT IS IGNORED
    type: fix
    value: FIXED_VALUE
  - type: vary
    comment: THIS TEXT IS IGNORED
    values:
      VARY_NAME: [VARY_VALUE1, VARY_VALUE2]
```

## Examples

### Only fixed parameters

```yaml
parameters:
  - R0: 3.0
  - infectious_period: 1.0
  - p_infected_initial: 0.001
```

This produces only a single parameter set:

```json
[
  {"R0": 3.0, "infectious_period": 1.0, "p_infected_initial": 0.001}
]
```

### A 2-dimensional grid with 1 fixed parameter

```yaml
parameters:
  - R0: {vary: [2.0, 3.0]}
  - infectious_period: {vary: [0.5, 2.0]}
  - p_infected_initial: 0.001
```

A 2-dimensional grid, with 2 values per dimension, produces 4 parameter sets:

```json
[
  {"R0": 2.0, "infectious_period": 0.5, "p_infected_initial": 0.001},
  {"R0": 2.0, "infectious_period": 2.0, "p_infected_initial": 0.001},
  {"R0": 3.0, "infectious_period": 0.5, "p_infected_initial": 0.001},
  {"R0": 3.0, "infectious_period": 2.0, "p_infected_initial": 0.001}
]
```

Note that the ordering of the outputs is not guaranteed.

### Replicate runs

If you want to run many replicates of each of those parameter sets, specify `seed` and `n_replicates`:

```yaml
parameters:
  - seed: 42
  - n_replicates: 100
  - p_infected_initial: 0.001
  - R0: {vary: [2.0, 3.0]}
  - infectious_period: {vary: [0.5, 2.0]}
```

This will still produce 4 parameter sets. It will be up to your wrapped simulation function to know how to run all the replicates. The `replicated()` function in this package is designed for that.

### 2-dimensional grid with multiple parameters in a dimension

```yaml
parameters:
  - type: vary
    values:
      R0: [2.0, 4.0]
      p_infected_initial: [0.01, 0.0001]
  - infectious_period: {vary: [0.5, 2.0]}
```

$R_0$ and $p_{I0}$ vary together, and the infectious period $1/\gamma$ varies separately, producing 4 parameter sets:

1. $R_0=2$, $p_{I0}=10^{-2}$, $1/\gamma=0.5$
2. $R_0=2$, $p_{I0}=10^{-2}$, $1/\gamma=2$
3. $R_0=4$, $p_{I0}=10^{-4}$, $1/\gamma=0.5$
4. $R_0=4$, $p_{I0}=10^{-4}$, $1/\gamma=2$

### Conditioned varying parameter

Vary over two states, matching with their capitals, and then also vary over beach towns in the coastal state:

```yaml
parameters:
  - type: vary
    values:
      state: [Virginia, North Dakota]
      capital: [Richmond, Pierre]
  - type: vary
    if: {state: Virginia}
    values:
      beach_town: [Virginia Beach, Chincoteague, Colonial Beach]
```

This produces 4 parameter sets. Note that `"beach_town"` is only present when `"state"` is `"Virginia"`:

```json
[
  {"state": "Virginia", "capital": "Richmond", "beach_town": "Virginia Beach"},
  {"state": "Virginia", "capital": "Richmond", "beach_town": "Chincoteague"},
  {"state": "Virginia", "capital": "Richmond", "beach_town": "Colonial Beach"},
  {"state": "North Dakota", "capital": "Pierre"}
]
```
