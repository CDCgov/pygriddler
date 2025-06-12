# Core concepts

There is no common nomenclature for the problem griddler solves, so we [make up our own](https://xkcd.com/927/). There are 3 core entities in griddler:

- A _parameter_ is a paired name and value, encoding an idea like "the reproduction number is 1.2."
- A _specification_ is a set (i.e., unordered list) of parameters. A specification can be all the variables and other configuration required to specify and run a single simulation.
- An _experiment_ is a set of specifications. An experiment might include replicate experiments with different random seeds, simple grids of parameter values (hence, "griddler"), or more complex combinations of parameters.

And there are 2 core operations:

- The _union_ of two experiments, which is just the union of the sets of parameter specifications, is another experiment.
- The _product_ of two experiments, similar to a Cartesian product, is another experiment consisting of the unions of all possible pairs of specifications formed by taking one specification from each of the two experiments.

These operations, combined in different ways, are sufficient to produce all sorts of experiments!

## Implementation

In the `griddler` package, parameters are key-value pairs in a `Spec` object, which is an extention of a dictionary with the requirement that the keys be strings. The `Experiment` class supports union via the `|` operator and product via `*`.

See the [API reference](reference.md) for more details.
