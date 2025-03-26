# griddle v0.2 specification

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
