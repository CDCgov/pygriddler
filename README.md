# Griddler: making grids of parameters

Griddler is a tool for converting human-written simulation experiment parameterizations, called "griddles," into sets of machine-readable parameter sets.

## Griddles

Griddles have a specific syntax. In this trivial example:

```yaml
version: v0.3
parameters:
  R0: { fix: 1.0 }
```

We get a single output parameter set:

```json
[{ "R0": 1.0 }]
```

Griddler supports **varying multiple parameters** over a grid:

```yaml
version: v0.3
parameters:
  R0: { vary: [1.5, 2.0] }
  gamma: { vary: [0.3, 0.4] }
```

produces 4 output parameter sets, with all combinations of input varying parameters:

```json
[
  { "R0": 1.5, "gamma": 0.3 },
  { "R0": 1.5, "gamma": 0.4 },
  { "R0": 2.0, "gamma": 0.3 },
  { "R0": 2.0, "gamma": 0.4 }
]
```

Griddler supports **bundles of parameters that vary together** (e.g., to produce scenarios):

```yaml
version: v0.3
parameters:
  scenario:
    vary:
      R0: [low, high]
      gamma: [low, high]
```

produces only 2 outputs:

```json
[
  { "R0": "low", "gamma": "low" },
  { "R0": "high", "gamma": "high" }
]
```

Griddle **conditional parameters**, allowing for subgridding:

```yaml
version: v0.3
parameters:
  method: { vary: [newton, brent] }
  start_point:
    if: { equals: { method: newton } }
    vary: [0.25, 0.50, 0.75]
  bounds:
    if: { equals: { method: brent } }
    fix: [0.0, 1.0]
```

which produces 4 parameter sets:

```json
[
  { "method": "newton", "start_point": 0.25 },
  { "method": "newton", "start_point": 0.5 },
  { "method": "newton", "start_point": 0.75 },
  { "method": "brent", "bounds": [0.0, 1.0] }
]
```

### Griddle template

```yaml
version: v0.3
parameters:
  # fixed parameter
  NAME1: { fix: VALUE }
  # single varying parameter
  NAME2: { vary: [VALUE, VALUE] }
  # varying bundle
  BUNDLE:
    NAME3: [VALUE, VALUE]
    NAME4: [VALUE, VALUE]
  # conditions and comments
  NAME5:
    fix: VALUE
    if: { equals: { NAME: VALUE } }
    comment: COMMENT
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

You should have received a copy of the Apache Software License along with this program. If not, see http://www.apache.org/licenses/LICENSE-2.0.html

The source code forked from other open source projects will inherit its license.

## Privacy Standard Notice

This repository contains only non-sensitive, publicly available data and information. All material and community participation is covered by the [Disclaimer](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md) and [Code of Conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md). For more information about CDC's privacy policy, please visit [http://www.cdc.gov/other/privacy.html](https://www.cdc.gov/other/privacy.html).

## Contributing Standard Notice

Anyone is encouraged to contribute to the repository by [forking](https://help.github.com/articles/fork-a-repo) and submitting a pull request. (If you are new to GitHub, you might start with a [basic tutorial](https://help.github.com/articles/set-up-git).) By contributing to this project, you grant a world-wide, royalty-free, perpetual, irrevocable, non-exclusive, transferable license to all users under the terms of the [Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or later.

All comments, messages, pull requests, and other submissions received through CDC including this GitHub page may be subject to applicable federal law, including but not limited to the Federal Records Act, and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

## Records Management Standard Notice

This repository is not a source of government records but is a copy to increase collaboration and collaborative potential. All government records will be published through the [CDC web site](http://www.cdc.gov).
