# griddler

Griddles are the main functionality of griddle. Read about the [griddle schema](griddles.md) to learn more about the format.

## Getting started 

### Command-line usage

Griddler can be used from the command line with any language. It reads a YAML (or JSON)
griddle definition and writes the expanded parameter sets as JSON.

You can install it from GitHub with `uv` or another git-backed package maanger:

```bash
uv tool install git+https://github.com/cdcgov/griddler.git
```

Example usage:

```bash
griddler my_griddle.yaml > my_parameter_sets.json
```

Use the `--help` flag for more details.

### Python API

You can also directly generate a griddle directly in Python:

```bash
uv add git+https://github.com/cdcgov/griddler.git
```

```python
import yaml

import griddler

with open("my_griddle.yaml") as f:
    raw_griddle = yaml.safe_load(f)

griddle = griddler.Griddle(raw_griddle)
parameter_sets = griddle.parse()
```

See the [API reference](api.md) for specifics on griddler's internals.

