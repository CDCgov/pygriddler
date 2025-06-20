# Core concepts

There is no common nomenclature for the problem griddler solves, so we [make up our own](https://xkcd.com/927/). There are 2 core concepts in griddler: the _Spec_ and the _Experiment_.

A Spec is a collection of parameter values. Informally, it is a set of parameter name-value pairs. Typically, a Spec corresponds to the variables and other configuration required to specify and run a single simulation. One Spec can be _updated_ by another one, creating a new Spec with values from the updating Spec.

An Experiment is a set of Specs. An Experiment might include replicate simulations with different random seeds, simple grids of parameter values (hence, "griddler"), or more complex combinations of parameters. Experiments support two operations:

- The _union_ of two Experiments, which is just the union of the their constituent Specs, is another Experiment.
- The _product_ of two Experiments, similar to a Cartesian product, is another Experiment formed by taking each Spec in one Experiment and updating it with each Spec in the other Experiment.

Experiments, combined with unions and products, are sufficient to produce all sorts of simulations!

## Implementation

In the `griddler` package, Specs are just dictionaries, which have the `update` (or `|`) operation. Experiments are objects of the `Experiment` class. Each `Experiment` holds a set of Specs, supports `.union()` (or `|`) and `.product()` (or `*`).

See the [API reference](api.md) for more details.

## Theory

Mathematically speaking, Specs are their operation are a [monoid](https://en.wikipedia.org/wiki/Monoid), while Experiments and their operations are a [hemiring](https://en.wikipedia.org/wiki/Semiring#Generalizations). Specifically, a Spec $\vec{x} = (x_1, \ldots, x_N)$ is a tuple, where $N$ is the total number of parameters we will be interested in. ($N$ may be greater than the number of parameters with assigned values in any particular Spec.) The space of the $x_i$ includes all possible parameter values as well as an additional neutral element $0_M$. The $x_i$ have a single binary operation _update_ $\oplus$ that returns the right element, unless that element is the neutral element:

```math
x \oplus y = \begin{cases}
x & y = 0_M \\
y & \text{otherwise}
\end{cases}
```

Note the values and the operation $\oplus$ form a monoid, not a [group](<https://en.wikipedia.org/wiki/Group_(mathematics)>), because the $\oplus$ operation lacks an inverse (i.e., for all $x \neq 0_M$, there is no $x^{-1}$ such that $x \oplus x^{-1} = 0_M$). Note also that this monoid is not commutative (i.e., $x \oplus y \neq y \oplus x$ in general).

Specs have an analogous update operation that is the element application of the value-wise update operation:

```math
\vec{x} \oplus \vec{y} = (x_1 \oplus y_1, \ldots, x_N \oplus y_N)
```

Thus, Specs and their $\oplus$ operator also form a monoid.

In the Python implementation, Specs are implemented as dictionaries. Dictionaries are indexed by parameter names rather than integers $i$ to index the values, and the neutral element $0_M$ is represented by the absence of that key from the dictionary.

An Experiment is a set of Specs, equipped with two operations: _union_ $\cap$, which is just the union of the sets of Specs, and _product_ $\otimes$, analogous to Cartesian product. For two experiments $X$ and $Y$, define $X \otimes Y = \{\vec{x} \oplus \vec{y} : \vec{x} \in X, \vec{y} \in Y\}$.

Experiments and their operations form a hemiring. Union $\cap$ is a commutative monoid, whose identity element is the empty Experiment $\varnothing$. Product $\otimes$ is a semigroup: it is associative but has no identity element. (Experiments do not form a semiring because of this absence of an identity element for the product operation.)

Note that, similar to a ring, product $\otimes$ is commutative, and product with the union identity always returns that identity: $X \otimes \varnothing = \varnothing$ for any Experiment $X$.
