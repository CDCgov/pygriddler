# The griddle schema

Griddler is a tool for parsing a *griddle* to produce an array of *parameter sets*.

A *parameter* consists of a string *name* and a *value* of arbitrary type. A *parameter set* is an object whose keywords are the parameter names and whose values are the corresponding parameter values.

!!! note

    This document uses JSON typing nomenclature. A JSON array is like a Python list. A JSON object is a Python dictionary. An object keyword is like a dictionary key.


A *griddle* is an object with two keywords: `version` and `parameters`. `version` specifies the version of the griddler schema, currently `"v0.3"`. `parameters` is an object whose keywords are usually parameter names and whose values are parameter *specifications*. Each specification specifies one of:

1. a *fixed* parameter that appears in every parameter set (so long as it is not *conditioned*) with the same value,
2. a *varying bundle* of parameters that takes on different values in different parameters sets.

In typical practice, griddles are read in from YAML or JSON files, and parameter sets are serialized as JSON files. That convention is used in the examples here.

## Minimal griddle

The minimal functional griddle has a version and no parameters.

```yaml
version: v0.3
parameters: {}
```

## Fixed parameters

```yaml
version: v0.3
parameters:
  NAME:
    fix: VALUE
  # note that this could be written in YAML as:
  # NAME: {fix: VALUE}
```

In this and future examples, capitals are used to designate values that would be filled in. In future examples, `version` is omitted for brevity.

Note that the value of a fixed parameter need not be a scalar. For example, `delay_distribution_pmf` would appear as the same array in all the parameter sets:

```yaml
parameters:
  delay_distribution_pmf: {fix: [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0]}
```

## Varying bundles of parameters

The canonical form is:

```yaml
parameters:
  NAME:
    vary:
      NAME1: [NAME1_VALUE1, NAME1_VALUE2] # and so on for NAME1_VALUE3, etc.
      NAME2: [NAME2_VALUE1, NAME2_VALUE2]
      # and so on for NAME3, etc.
```

The parameters `NAME1` and `NAME2` are in a *bundle* because they will vary together across parameter sets. In the parameter sets, `NAME1` will take on the `NAME1_VALUE*` values, `NAME2` will take on the `NAME2_VALUE*` values, and so forth. The `*_VALUE1` values will always appear together, the `*_VALUE2` will always appear together, and so forth, so the values lists must all be of equal length. The top-level `NAME`, a unique identifier for the bundle of parameters `NAME1`, `NAME2`, etc. does not appear in the parameter sets.

## Single varying parameters

If there is only one parameter in a bundle, griddler support a short form:

```yaml
parameters:
  NAME:
    vary: [VALUE1, VALUE2]
  # note that this could be written in YAML as:
  # NAME: {vary: [VALUE1, VALUE2]}
```

The top-level `NAME` is used as the parameter name.

### Conditioned parameters

A conditioned parameter will only be present in a parameter set when some one or more other parameters are present and have some particular values.

```yaml
parameters:
  FIXED_NAME:
    if: {COND_NAME1: COND_VALUE1, COND_NAME2: COND_VALUE2}
    fix: VALUE

  VARYING_BUNDLE_NAME:
    if: {COND_NAME1: COND_VALUE1, COND_NAME2: COND_VALUE2}
    vary:
      VARYING_PARAM_NAME: [VALUE1, VALUE2]

  VARYING_PARAM_NAME:
    if: {COND_NAME1: COND_VALUE1, COND_NAME2: COND_VALUE2}
    vary: [VALUE1, VALUE2]
```

## Comments

Any content in a `comment` field is ignored. This is not important in YAML files, which have native comments, but can be useful in a human-written JSON. Comments are only available in canonical forms.

```yaml
parameters:
  FIXED_NAME:
    comment: THIS TEXT IS IGNORED
    fix: VALUE
  VARYING_PARAM_NAME:
    comment: THIS TEXT IS IGNORED
    vary: [VARY_VALUE1, VARY_VALUE2]
```

## Examples

### Only fixed parameters

```yaml
parameters:
  R0: {fix: 3.0}
  infectious_period: {fix: 1.0}
  p_infected_initial: {fix: 0.001}
```

This produces only a single parameter set:

```json
[
  {"R0": 3.0, "infectious_period": 1.0, "p_infected_initial": 0.001}
]
```

### 2 varying parameters and 1 fixed

```yaml
parameters:
  - R0: {vary: [2.0, 3.0]}
  - infectious_period: {vary: [0.5, 2.0]}
  - p_infected_initial: {fix: 0.001}
```

This produces 4 parameter sets:

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
  seed: {fix: 42}
  n_replicates: {fix: 100}
  p_infected_initial: {fix: 0.001}
  R0: {vary: [2.0, 3.0]}
  infectious_period: {vary: [0.5, 2.0]}
```

This will still produce 4 parameter sets. It will be up to your wrapped simulation function to know how to run all the replicates. The `replicated()` function in this package is designed for that.

### Varying parameter bundles

```yaml
parameters:
  scenario:
    vary:
      R0: [2.0, 4.0],
      p_infected_initial: [0.01, 0.0001]
  infectious_period: {vary: [0.5, 2.0]}
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
  state_and_capital:
    vary:
      state: [Virginia, North Dakota]
      capital: [Richmond, Pierre]
  beach_town:
    if: {state: Virginia}
    vary: [Virginia Beach, Chincoteague, Colonial Beach]
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
