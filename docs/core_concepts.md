# Core concepts

There is no common nomenclature for the problem griddler solves, so we [make up our own](https://xkcd.com/927/). There are 3 core entities in griddler:

- A _Parameter_ is a paired name and value, encoding an idea like "the reproduction number is 1.2." (Lower-case "parameter" and "parameterization" are used as non-specific, common sense terms.)
- A _Specification_ is a set (i.e., unordered list) of Parameters. A Specification can be all the variables and other configuration required to specify and run a single simulation.
- An _Experiment_ is a set of Specifications. An Experiment might include replicate simulations with different random seeds, simple grids of parameter values (hence, "griddler"), or more complex combinations of parameters.

And there are 2 core operations:

- The _union_ of two Experiments, which is just the union of the their constituent Specifications, is another Experiment.
- The _product_ of two Experiments, similar to a Cartesian product, is another Experiment consisting of the unions of all possible pairs of Specifications formed by taking one Specification from each of the two Experiments. This requires that all pairs of Specifications are _disjoint_, that is, that they share no Parameters with the same name.

These operations, combined in different ways, are sufficient to produce all sorts of simulations!

## Implementation

In the `griddler` package, Parameters are implemented key-value pairs in a `Spec` object, which is an extention of a dictionary with the requirement that the keys be strings. The `Experiment` class, which holds a set of `Spec` objects, supports union via the `|` operator and product via `*`.

See the [API reference](api.md) for more details.

## Theory

Mathematically speaking, Experiments are [hemirings](https://en.wikipedia.org/wiki/Semiring#Generalizations), and Specifications and Parameter values are [monoids](https://en.wikipedia.org/wiki/Monoid). To see this, replace the informal definitions above with more rigorous ones.

A Specification $\vec{x} = (x_1, \ldots, x_N)$ is a tuple of Parameter values $x_i$, where $N$ is the total number of parameter names we will be interested in. ($N$ may be greater than the number of parameters with assigned values in any particular Specification.) The space of the $x_i$ includes all possible parameter values as well as an additional neutral element $0_M$. The $x_i$ have a single binary operation _update_ $\oplus$ that returns the right element, unless that element is the neutral element:

```math
x \oplus y = \begin{cases}
x & y = 0_M \\
y & \text{otherwise}
\end{cases}
```

Note that this structure is a monoid, not a [group](<https://en.wikipedia.org/wiki/Group_(mathematics)>), because the update operation lacks an inverse (i.e., for all $x \neq 0_M$, there is no $x^{-1}$ such that $x \oplus x^{-1} = 0_M$). Note also that this monoid is not commutative (i.e., $x \oplus y \neq y \oplus x$ in general).

Specifications have an analogous, elementwise "update" operation, and are therefore also a monoid:

```math
\vec{x} \oplus \vec{y} = (x_1 \oplus y_1, \ldots, x_N \oplus y_N)
```

In the Python implementation, Specifications are implemented as dictionaries:

- Specifications are indexed by parameter names rather than integers $i$ to index the values.
- The neutral element $0_M$ is represented by the absence of that key from the dictionary.
- The Specification's update $\oplus$ operation is implemented by the dictionary's [`update`](https://docs.python.org/3/library/stdtypes.html#dict.update) method, which is also written `|`.

An Experiment is a set of Specifications, equipped with two operations: _union_ $\cup$, which is the union of the sets of Specifications, and _product_ $\otimes$, analogous to Cartesian product. For two experiments $X$ and $Y$, define $X \otimes Y = \{\vec{x} \oplus \vec{y} : \vec{x} \in X, \vec{y} \in Y\}$.

This structure is a hemiring. Union $\cup$ is a commutative monoid, whose identity element is the empty Experiment $\varnothing$. Product $\otimes$ is a semigroup: it is associative but has no identity element. (Experiments do not form a semiring because of this absence of an identity element for the product operation.)

Note that, similar to a ring, product $\otimes$ is commutative, and product with the union identity always returns that identity: $X \otimes \varnothing = \varnothing$ for any Experiment $X$.
