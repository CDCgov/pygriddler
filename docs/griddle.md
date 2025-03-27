# The griddle format

## Versioning

This doc describes the latest specification. Previous specifications:

- [v0.2](griddle_0_2.md)

## Specification

Griddler is a tool for parsing *griddles* to produce a list of *parameter sets*.

A griddle is a Python list. Each element is a dictionary representing a *fixed parameter* or a *grid dimension*. Fixed parameters and grid dimensions can be *conditioned*.

A parameter set is a dictionary who keys are parameter names, of string type, and whose values are the values of the corresponding parameters.

In typical practice, griddles are read in from YAML or JSON files, and the resulting parameter sets are serialized as JSON files. That convention is used in the specifications and examples here.

### Fixed parameter

A fixed parameter is a parameter that has the same value in all parameter sets (unless it is conditioned). The canonical form is:

```yaml
- name: parameter_name
  type: fix
  value: parameter_value
```

Griddler supports a short form, so long as parameter name is not a reserved word (`name`, `type`, `value`, `values`, `if`, `comment`):

```yaml
- parameter_name: parameter_value
```

Note that the value of a fixed parameter need not be a scalar. In this example `delay_distribution_pmf` will appear as the same list of values in all the parameter sets:

```yaml
- delay_distribution_pmf: [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0]
```

### Grid dimension

A grid dimension is one or more parameters that take on different values in different parameter sets. All combinations of all grid dimensions are present in the output parameter sets (unless the dimension is conditioned).

The canonical form is:

```yaml
- type: vary
  values:
  - name: parameter_name1
    values: [param1_value1, param1_value2]
  - name: parameter_name2
    values: [param2_value1, param2_value2]
```

In the parameter sets, `param1_value1`, `param2_value1`, etc. will always appear together, and `param1_value2`, `param2_value2`, etc. will always appear together.

Griddler support a short form, which assumes that the parameter names are not one of the reserved words:

```yaml
- type: vary
  values:
    parameter_name1: [param1_value1, param1_value2]
    parameter_name2: [param2_value1, param2_value2]
```

For a grid dimension that has only one parameter, whose name is not a reserved word, griddler supports an additional short form:

```yaml
- parameter_name: {vary: [value1, value2]}
```

### Conditioned parameters

A conditioned parameter will only be present in an parameter set when some one or more other parameters are present and have some particular values.

```yaml
# conditioned fixed parameter, canonical form
- name: conditioned_parameter_name
  if: {parameter_name1: parameter_value1, parameter_name2: parameter_value2}
  type: fix
  value: conditioned_parameter_value

# (there is no short form for conditioned fixed parameter)

# conditioned varying parameter, canonical form
- type: vary
  if: {parameter_name1: parameter_value1, parameter_name2: parameter_value2}
  values:
    - name: varying_parameter_name1
      values: [v_param_value1, v_param_value2]

# conditioned varying parameter, short form
- type: vary
  if: {parameter_name1: parameter_value1, parameter_name2: parameter_value2}
  values:
    varying_parameter_name1: [v_param_value1, v_param_value2]
```

### Comments

Any content in these fields are ignored. This is not important in YAML files, which support comments, but can be useful in a human-written JSON.

```yaml
- name: fixed_parameter_name
  type: fix
  value: fixed_parameter_value
  comment: Whatever is here is ignored
- type: vary
  comment: Whatever is here is ignored
  values:
    varying_parameter: [varying_value1, varying_value2]
```

### Version

TBD: A way to specify which version/schema the file is from.

## Examples

### Only fixed parameters

```yaml
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
- seed: 42
- n_replicates: 100
- p_infected_initial: 0.001
- R0: {vary: [2.0, 3.0]}
- infectious_period: {vary: [0.5, 2.0]}
```

This will still produce 4 parameter sets. It will be up to your wrapped simulation function to know how to run all the replicates. The `replicated()` function in this package is designed for that.

### 2-dimensional grid with multiple parameters in a dimension

```yaml
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
