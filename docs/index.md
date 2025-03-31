# griddler

Griddles are the main functionality of griddle. Read about the [griddle schema](griddle.md) to get started.

## Using griddler from the command line

Griddler can also be used on the command line to read an input YAML (or JSON) and write output JSON:

```
python -m griddler my_griddle.yaml > my_parameter_sets.json
```

Use the `--help` flag for more details.

## Using griddle in other python projects

You can generate a griddle directly in Python:

```python
import yaml

import griddler

with open("my_griddle.yaml") as f:
    raw_griddle = yaml.safe_load(f)

griddle = griddler.Griddle(raw_griddle)
parameter_sets = griddle.parse()
```

See the the [API reference](reference.md) for specifics on griddler's internals.
