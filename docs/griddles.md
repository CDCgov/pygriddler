# Griddles

For complex Experiments, you might want to write a Python file that manipulates `Spec` and `Experiment` objects directly. See the [API reference](api.md) for more details.

For simpler Experiments, griddler supports _griddles_. A griddle is a dictionary, usually read in from a human-written file like a YAML or JSON, that specifies the _schema_ and then whatever is needed to uniquely specify the Experiment. (Technically, a griddle is a Python dictionary, but we might also loosely refer to the YAML or JSON file as a "griddle.")

Every griddle must have the keyword `"schema"` and an associated string value that specifies how the griddle should be parsed into an Experiment. Beyond that, each schema can specify different requirements for the griddle format.

The currently-supported griddle schemas are:

- v0.4

## Schemas

### v0.4

Schema `v0.4` adheres as close as possible to the underlying griddler logic while not actually requiring any Python. The trivial example is:

```yaml
schema: v0.4
experiment: []
```

This returns an empty Experiment (i.e., containing zero Specs). The minimal example, of a single, fixed parameter is:

```yaml
schema: v0.4
experiment: [{ R0: 1.0 }]
```

This produces an Experiment with a single Spec. Serialized as JSON:

```json
[{ "R0": 1.0 }]
```

An example of the product might be:

```yaml
schema: v0.4
experiment:
  product:
    - [{ R0: 1.5 }, { R0: 2.0 }]
    - [{ gamma: 0.3 }, { gamma: 0.4 }]
```

which produces 4 Specs, with all combinations of input varying parameters:

```json
[
  { "R0": 1.5, "gamma": 0.3 },
  { "R0": 1.5, "gamma": 0.4 },
  { "R0": 2.0, "gamma": 0.3 },
  { "R0": 2.0, "gamma": 0.4 }
]
```

Unions become useful when combining Experiments that vary different parameters. For example, an Experiment might consist of some simulations where a simulated quantity follows the normal distribution and other simulations where it follows the gamma distribution. For the normal distribution simulations, we might want to grid over values of the mean and standard deviation, while in the gamma distribution simulations, we want to grid over shape and scale parameters:

```yaml
schema: v0.4
experiment:
  product:
    - [{ R0: 1.5 }]
    - union:
        - product:
            - [{ distribution: normal }]
            - [{ mean: 0.5 }, { mean: 1.0 }, { mean: 1.5 }]
            - [{ sd: 0.5 }, { sd: 1.0 }]
        - product:
            - [{ distribution: gamma }]
            - [{ shape: 0.5 }, { shape: 1.0 }]
            - [{ scale: 0.5 }, { scale: 1.0 }]
```

which produces multiple Specs:

```json
[
  { "R0": 1.5, "distribution": "normal", "mean": 0.5, "sd": 0.5 },
  { "R0": 1.5, "distribution": "normal", "mean": 0.5, "sd": 1.0 },
  { "R0": 1.5, "distribution": "normal", "mean": 1.0, "sd": 0.5 },
  // etc. with further mean/sd combinations
  { "R0": 1.5, "distribution": "gamma", "shape": 0.5, "scale": 0.5 }
  // etc. with further shape/scale combinations
]
```

#### Syntax

The `v0.4` schema has syntax:

```yaml
schema: v0.4
experiment: <experiment>
```

where the experiment has syntax:

```text
<experiment> ::= [{<key>: <value>, ...}, ...]
                 | {"union": [<experiment>, ...]}
                 | {"product": [<experiment>, ...]}
```

### v0.3

The v0.3 syntax is designed to for simple combinations of fixed and varying parameters.

#### Minimal griddle

The minimal functional griddle has a schema and no parameters.

```yaml
schema: v0.3
parameters: {}
```

#### Fixed parameters

A fixed parameter has the same value in all Specs (unless the parameter is _conditioned_).

```yaml
schema: v0.3
parameters:
  NAME:
    fix: VALUE
  # note that this could be written in YAML as:
  # NAME: {fix: VALUE}
```

In this and future examples, capitals are used to designate values that would be filled in. In future examples, `schema` is omitted for brevity.

Note that the value of a fixed parameter need not be a scalar. For example, `delay_distribution_pmf` would appear as the same array in all the parameter sets:

```yaml
parameters:
  delay_distribution_pmf: { fix: [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0] }
```

#### Varying parameter

A varying parameter takes on different values in different Specs. In the absence of conditioning or bundling, all combinations of all varying parameters will appear in the output.

```yaml
parameters:
  NAME:
    vary: [VALUE1, VALUE2]
  # note that this could be written in YAML as:
  # NAME: {vary: [VALUE1, VALUE2]}
```

#### Varying bundles of parameters

In a _varying bundle_ of parameters, multiple parameters take on different values in different data sets, but those parameters vary together.

```yaml
parameters:
  BUNDLE_NAME:
    vary:
      NAME1: [NAME1_VALUE1, NAME1_VALUE2] # and so on for NAME1_VALUE3, etc.
      NAME2: [NAME2_VALUE1, NAME2_VALUE2]
      # and so on for NAME3, etc.
```

In the parameter sets, `NAME1` will take on the `NAME1_VALUE*` values, `NAME2` will take on the `NAME2_VALUE*` values, and so forth. The `*_VALUE1` values will always appear together, the `*_VALUE2` will always appear together, and so forth, so the values lists must all be of equal length. `BUNDLE_NAME` is a unique identifier for the bundle of parameters `NAME1`, `NAME2`, etc. and does not appear in the parameter sets. `BUNDLE_NAME` cannot be the same as any parameter name.

Note that a single varying parameter could be written as:

```yaml
parameters:
  BUNDLE_NAME:
    vary:
      NAME: [VALUE1, VALUE2]
```

with the caveat that `BUNDLE_NAME` and `NAME` cannot be the same.

#### Conditioned parameters

A _conditioned_ parameter will only be present in a parameter set when some one or more other parameters are present and take on some particular values. A the value associated with the `if` keyword is a _condition_ that evaluates to true or false.

For now, the only supported conditions are:

1. `{}`, which is always true, and
2. a test for equality of a single parameter to a single value: `{equals: {COND_NAME: COND_VALUE}}`.

```yaml
parameters:
  FIXED_NAME:
    fix: VALUE
    if: true

  VARYING_NAME:
    vary:
      VARYING_PARAM_NAME: [VALUE1, VALUE2]
    if: { equals: { COND_NAME: COND_VALUE } }
```

Conditioned parameters are evaluated after unconditioned parameters, but the order of their evaluation is not guaranteed. Thus, a graph of dependent `if` statements is not supported.

#### Comments

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

#### Examples

##### Only fixed parameters

```yaml
parameters:
  R0: { fix: 3.0 }
  infectious_period: { fix: 1.0 }
  p_infected_initial: { fix: 0.001 }
```

This produces only a single parameter set:

```json
[{ "R0": 3.0, "infectious_period": 1.0, "p_infected_initial": 0.001 }]
```

##### 2 varying parameters and 1 fixed

```yaml
parameters:
  - R0: { vary: [2.0, 3.0] }
  - infectious_period: { vary: [0.5, 2.0] }
  - p_infected_initial: { fix: 0.001 }
```

This produces 4 parameter sets:

```json
[
  { "R0": 2.0, "infectious_period": 0.5, "p_infected_initial": 0.001 },
  { "R0": 2.0, "infectious_period": 2.0, "p_infected_initial": 0.001 },
  { "R0": 3.0, "infectious_period": 0.5, "p_infected_initial": 0.001 },
  { "R0": 3.0, "infectious_period": 2.0, "p_infected_initial": 0.001 }
]
```

Note that the ordering of the outputs is not guaranteed.

##### Varying parameter bundles

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

##### Conditioned varying parameter

Vary over two states, matching with their capitals, and then also vary over beach towns in the coastal state:

```yaml
parameters:
  state_and_capital:
    vary:
      state: [Virginia, North Dakota]
      capital: [Richmond, Pierre]
  beach_town:
    if: { equals: { state: Virginia } }
    vary: [Virginia Beach, Chincoteague, Colonial Beach]
```

This produces 4 parameter sets. Note that `"beach_town"` is only present when `"state"` is `"Virginia"`:

```json
[
  {
    "state": "Virginia",
    "capital": "Richmond",
    "beach_town": "Virginia Beach"
  },
  { "state": "Virginia", "capital": "Richmond", "beach_town": "Chincoteague" },
  {
    "state": "Virginia",
    "capital": "Richmond",
    "beach_town": "Colonial Beach"
  },
  { "state": "North Dakota", "capital": "Pierre" }
]
```

### v0.2

The v0.2 syntax is described in [historical docs](https://github.com/CDCgov/pygriddler/blob/v0.2/docs/griddle.md). It is not currently supported.
