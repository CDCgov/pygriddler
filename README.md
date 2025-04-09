# Griddler: making grids of parameters

Griddler is a tool for converting *griddles*, which are human-written files for specifying simulation experiments, into lists of machine-readable parameter specifications.

An *experiment* is a set (or list, with the understanding that the order is not guaranteed) of *parameter specifications*. A parameter specification is a set of parameter name-value pairs (e.g., implemented as a JSON object or a Python dictionary.)

## Griddles

A griddle, typically written in YAML, consists of some metadata and an *experiment specification*. The experiment specification can be the experiment itself, that is, the list of parameter specs. Thus, the trivial example is:

```yaml
version: v0.3
experiment: []
```

This returns an empty list `[]` of parameter specifications. The minimal example, of a single, fixed parameter is:

```yaml
version: v0.3
experiment: [{R0: 1.0}]
```

We get a single output parameter set, serialized as JSON:

```json
[
    {"R0": 1.0}
]
```

The power of griddler is in taking *products* and *unions* over experiments. The product of two experiments is the Cartesian product of their constitutent parameter specs. For example:

```yaml
version: v0.3
experiment:
  product:
    - [{R0: 1.5}, {R0: 2.0}]
    - [{gamma: 0.3}, {gamma: 0.4}]
```

which produces 4 output parameter sets, with all combinations of input varying parameters:

```json
[
    {"R0": 1.5, "gamma": 0.3},
    {"R0": 1.5, "gamma": 0.4},
    {"R0": 2.0, "gamma": 0.3},
    {"R0": 2.0, "gamma": 0.4}
]
```

Unions become useful when combining experiments that vary different parameters. For example, an experiment might consist of some simulations where a simulated quantity follows the normal distribution and other simulations where it follows the gamma distribution. For the normal distribution simulations, we might want to grid over values of the mean and standard deviation, while in the gamma distribution simulations, we want to grid over shape and scale parameters:

```yaml
version: v0.3
experiment:
  product:
    - [{R0: 1.5}]
    - union:
        - product:
          - [{distribution: normal}]
          - [{mean: 0.5}, {mean: 1.0}, {mean: 1.5}]
          - [{sd: 0.5}, {sd: 1.0}]
        - product:
          - [{distribution: gamma}]
          - [{shape: 0.5}, {shape: 1.0}]
          - [{scale: 0.5}, {scale: 1.0}]
```

which produces multiple parameter sets:

```json
[
  {"R0": 1.5, "distribution": "normal", "mean": 0.5, "sd": 0.5},
  {"R0": 1.5, "distribution": "normal", "mean": 0.5, "sd": 1.0},
  {"R0": 1.5, "distribution": "normal", "mean": 1.0, "sd": 0.5},
  // etc. with further mean/sd combinations
  {"R0": 1.5, "distribution": "gamma", "shape": 0.5, "scale": 0.5},
  // etc. with further shape/scale combinations
]
```

### Syntax summary

The griddle has syntax:

```yaml
version: v0.3
experiment:
  <experiment-spec>
```

where the experiment specification has syntax:

```text
<experiment-spec> ::= [<parameter-spec>, ...]
                       | {"union": [<experiment-spec>, ...]}
                       | {"product": [<experiment-spec>, ...]}
```

## Getting started

Use griddler from the command line:

```bash
python -m griddler my_griddle.yaml > parameter_sets.json
```

Or, from within Python:

```python
import yaml

import griddler

with open("my_griddle.yaml") as f:
    raw_griddle = yaml.safe_load(f)

griddle = griddler.Griddle(raw_griddle)
parameter_sets = griddle.parse()
```

See the [GitHub pages documentation](https://cdcgov.github.io/pygriddler/) for more detail. Source documentation is under `docs/`.

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
