# Griddler: a grammar of parameters

Griddler is a tool for converting human-written specifications for simulation experiments into lists of machine-readable specifications.

## Why griddler?

Modelers often want to run multiple simulations with different but related parameterizations. Some parameters should be in common across all simulations, while others should vary in patterns like "grids" or "bundles."

Griddler provides a grammar of these kinds of multiple parameterizations that aims to separate the specification of parameterizations from the running of simulations. Ideally, a user can write a single "[griddle](docs/griddle.md)" file (or, in more complex cases, a `griddle`-importing Python script) that produces all the different simulation parameterizations of interest.

## Getting started

Read the [GitHub pages documentation](https://cdcgov.github.io/pygriddler/)!

If you have a griddle written in a [supported schema](docs/griddles.md), the easiest way to use griddler is from the command line:

```bash
python -m griddler my_griddle.yaml > my_experiment.json
```

Or, from within Python:

```python
import griddler
import yaml

with open("my_griddle.yaml") as f:
    my_griddle = yaml.safe_load(f)

my_experiment = griddler.parse(my_griddle)
my_parameter_sets = my_experiment.to_dicts()
```

## Examples

For complex experiments, you might want to write a Python file that manipulates `Parameter`, `Spec`, and `Experiment` objects directly. See the [API reference](docs/api.md) for more details.

For simpler experiments, griddler supports multiple _griddle_ schemas. A griddle is a human-written file, usually a YAML or JSON, that contains some metadata and then whatever is needed to uniquely specify the experiment. See the [griddle](docs/griddles.md) for more details.

In the `v0.4` schema, the trivial example is:

```yaml
schema: v0.4
experiment: []
```

The minimal example of a single, fixed parameter is:

```yaml
schema: v0.4
experiment: [{ R0: 1.0 }]
```

The output, serialized as JSON, is:

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

which produces a list of 4 outputs, with all combinations of input varying parameters:

```json
[
  { "R0": 1.5, "gamma": 0.3 },
  { "R0": 1.5, "gamma": 0.4 },
  { "R0": 2.0, "gamma": 0.3 },
  { "R0": 2.0, "gamma": 0.4 }
]
```

Unions become useful when combining experiments that vary different parameters. For example, an experiment might consist of some simulations where a simulated quantity follows the normal distribution and other simulations where it follows the gamma distribution. For the normal distribution simulations, we might want to grid over values of the mean and standard deviation, while in the gamma distribution simulations, we want to grid over shape and scale parameters:

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

which produces multiple outputs:

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

## Project Admin

Scott Olesen <ulp7@cdc.gov> (CDC/IOD/ORR/CFA)

## Changelog

See the [repo releases](https://github.com/CDCgov/pygriddler/releases).

---

## General Disclaimer

This repository was created for use by CDC programs to collaborate on public health related projects in support of the [CDC mission](https://www.cdc.gov/about/organization/mission.htm). GitHub is not hosted by the CDC, but is a third party website used by CDC and its partners to share information and collaborate on software. CDC use of GitHub does not imply an endorsement of any one particular service, product, or enterprise.

## Public Domain Standard Notice

This repository constitutes a work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105. This repository is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/). All contributions to this repository will be released under the CC0 dedication. By submitting a pull request you are agreeing to comply with this waiver of copyright interest.

## License Standard Notice

This repository is licensed under ASL v2 or later.

This source code in this repository is free: you can redistribute it and/or modify it under the terms of the Apache Software License version 2, or (at your option) any later version.

This source code in this repository is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Apache Software License for more details.

You should have received a copy of the Apache Software License along with this program. If not, see <http://www.apache.org/licenses/LICENSE-2.0.html>

The source code forked from other open source projects will inherit its license.

## Privacy Standard Notice

This repository contains only non-sensitive, publicly available data and information. All material and community participation is covered by the [Disclaimer](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md) and [Code of Conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md). For more information about CDC's privacy policy, please visit [http://www.cdc.gov/other/privacy.html](https://www.cdc.gov/other/privacy.html).

## Contributing Standard Notice

Anyone is encouraged to contribute to the repository by [forking](https://help.github.com/articles/fork-a-repo) and submitting a pull request. (If you are new to GitHub, you might start with a [basic tutorial](https://help.github.com/articles/set-up-git).) By contributing to this project, you grant a world-wide, royalty-free, perpetual, irrevocable, non-exclusive, transferable license to all users under the terms of the [Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or later.

All comments, messages, pull requests, and other submissions received through CDC including this GitHub page may be subject to applicable federal law, including but not limited to the Federal Records Act, and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

## Records Management Standard Notice

This repository is not a source of government records but is a copy to increase collaboration and collaborative potential. All government records will be published through the [CDC web site](http://www.cdc.gov).
