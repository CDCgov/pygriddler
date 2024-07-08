# griddler

## Getting started

### Parsing griddles

At the command line, `griddler parse < griddle.yaml > parameter_sets.yaml` will read a "griddle" yaml and output a list of lists yaml.

In a script, the same could be accomplished with:
```python
parameter_sets = griddler.griddle.read("griddle.yaml")

with open("parameter_sets.yaml", "w") as f:
    yaml.dump(parameter_sets, f)
```

## Parameter hashing

A parameter set has a stable hash, implemented as a BLAKE2 digest of the JSON representation of the parameter set:
```python
>>> ParameterSet({"gamma": 1.0, "beta": 2.0}).stable_hash()
'2d220d93aff966ac7c50' # pragma: allowlist secret
```

## Future plans

# Problems

- Random number generators and parallelization (e.g., [this blog](https://albertcthomas.github.io/good-practices-random-number-generators/))
