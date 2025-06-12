# Core concepts

There is no common nomenclature for the problem griddler solves, so we [make up our own](https://xkcd.com/927/). There are 3 core entities in griddler:

- A _Parameter_ is a paired name and value, encoding an idea like "the reproduction number is 1.2."
- A _Specification_ is a set (i.e., unordered list) of Parameters. A Specification can be all the variables and other configuration required to specify and run a single simulation.
- An _Experiment_ is a set of Specifications. An Experiment might include replicate simulations with different random seeds, simple grids of parameter values (hence, "griddler"), or more complex combinations of parameters.

And there are 2 core operations:

- The _union_ of two Experiments, which is just the union of the their constituent Specifications, is another Experiment.
- The _product_ of two Experiments, similar to a Cartesian product, is another Experiment consisting of the unions of all possible pairs of Specifications formed by taking one Specification from each of the two Experiments. This requires that all pairs of Specifications are _disjoint_, that is, that they share no Parameters with the same name.

These operations, combined in different ways, are sufficient to produce all sorts of simulations!

## Implementation

In the `griddler` package, Parameters are key-value pairs in a `Spec` object, which is an extention of a dictionary with the requirement that the keys be strings. The `Experiment` class supports union via the `|` operator and product via `*`.

See the [API reference](api.md) for more details.
