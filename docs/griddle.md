# The griddle format

## Specification

- A griddle is YAML file, specifying a top-level dictionary.
  - The top-level dictionary have at least one of `baseline_parameters` or `grid_parameters` as a key.
  - If the top-level dictionary has `grid_parameters`, it may also have `nested_parameters` as a key.
  - It must not have any other keys.
- `baseline_parameters` is a dictionary.
  - The keys are parameter names; the values are parameter values.
  - A parameter value is valid if it is:
    - an integer, float, or string,
    - a list or tuple made up of integers, floats, or strings, or
    - a dictionary whose keys are strings and whose values are any valid parameter (i.e., scalar, list, or another valid dictionary).
- `grid_parameters` is a dictionary.
  - The keys are parameter names. Each value is a list. The elements in that list are the parameter values gridded over.
  - No keys can be repeated between `baseline_parameters` and `grid_parameters`.
- `nested_parameters` is a list (not a dictionary).
  - Each element is a dictionary, called a "nest."
  - Every nest have at least one key that appears in the grid.
  - Key in each nest must be either:
    1.  present in `grid_parameters` or `baseline_parameters` (but not both), _or_
    2.  present in each nest.

When parsed, the griddle expands into a list of dictionaries, each of which is a parameter set.

## Examples

In the simplest case, the griddle will produce one parameter set:

```yaml
baseline_parameters:
  R0: 3.0
  infectious_period: 1.0
  p_infected_initial: 0.001
```

But maybe you want to run simulations over a grid of parameters. So instead use `grid_parameters`:

```yaml
baseline_parameters:
  p_infected_initial: 0.001

grid_parameters:
  R0: [2.0, 3.0]
  infectious_period: [0.5, 2.0]
```

This will run 4 parameter sets, over the Cartesian product of the parameter values for $R_0$ and $1/\gamma$.

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

You cannot repeat a parameter name that is in `baseline_parameters` in `grid_parameters`, because it would be overwritten every time. But you can use `nested_parameters` to _sometimes_ overwrite a baseline parameter value:

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
