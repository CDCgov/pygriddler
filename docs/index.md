# griddler

Griddles are the main functionality of griddle. Read about the [griddle schema](griddles.md) to learn more about the format.

## Getting started

### Command-line usage

Griddler can be used from the command line with any language. It reads a YAML (or JSON) griddle definition and writes the expanded parameter sets as JSON.

You can install it from GitHub with `uv` or another git-backed package maanger:

```bash
uv tool install git+https://github.com/cdcgov/pygriddler.git
```

Example usage:

```bash
griddler my_griddle.yaml > my_parameter_sets.json
```

Use the `--help` flag for more details.

### Python API

You can also use griddler as a Python package:

```bash
uv add git+https://github.com/cdcgov/pygriddler.git
```

You can then generate and manipulate griddles:

```python
import yaml

import griddler

with open("my_griddle.yaml") as f:
    raw_griddle = yaml.safe_load(f)

parameter_sets = griddler.parse(raw_griddle)
```

See the [API reference](api.md) for specifics on griddler's internals.
