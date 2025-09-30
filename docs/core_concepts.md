# Core concepts

There is no common nomenclature for the problem griddler solves, so we [make up our own](https://xkcd.com/927/). There are 2 core concepts in griddler: the _Spec_ and the _Experiment_.

A Spec is a set of parameter name-value pairs. Typically, a Spec corresponds to the variables and other configuration required to specify and run a single simulation. One Spec can be _updated_ by another one, creating a new Spec with values from the updating Spec.

An Experiment is a set of Specs. An Experiment might include replicate simulations with different random seeds, simple grids of parameter values (hence, "griddler"), or more complex combinations of parameters. Experiments support two operations:

- The _union_ of two Experiments, which is just the union of the their constituent Specs, is another Experiment.
- The _product_ of two Experiments, similar to a Cartesian product, is another Experiment formed by taking each Spec in one Experiment and updating it with each Spec in the other Experiment.

Experiments, combined with unions and products, are sufficient to produce all sorts of simulations!

## Implementation

In the `griddler` package, Specs are just dictionaries, which have the `update` (or `|`) operation. Experiments are objects of the `Experiment` class. Each `Experiment` holds a set of Specs, supports `.union()` (or `|`) and `.product()` (or `*`).

See the [API reference](api.md) for more details.

## Theory

### Specs

Specifically, a Spec is a set of name-value pairs, i.e., two-element [sequences](https://en.wikipedia.org/wiki/Sequence). Specs have a single, binary operation _update_ $\uparrow$ that adds the parameters in the right input to the left input, preferring the right value when the same name is present in both Specs. For two Specs $S$ and $T$,

```math
\begin{align*}
S \uparrow T = &\{ (n, v) : (n, v) \in S \text{ and } n \in \pi(S) \backslash \pi(T) \} \\
&\cup \{ (n, v) : (n, v) \in T \text{ and } n \notin \pi(S) \backslash \pi(T) \} \\
\end{align*}
```

where $\pi(\cdot)$ is the set of names in a Spec (i.e., the first [projection map](<https://en.wikipedia.org/wiki/Projection_(set_theory)>)) and $\backslash$ is set difference.

(The update operation is similar to [null coalescence](https://en.wikipedia.org/wiki/Null_coalescing_operator), which prefers the left value.)

Specs and the update operation $\uparrow$ form a monoid because there is an identity element (i.e., the empty set $\varnothing$) and the operation is associative. Note that Specs are not commutative: the order of the inputs matters.

### Experiments

An Experiment is a set of Specs, equipped with two operations: _union_ $\cap$, which is just the union of the constituent sets of Specs, and _product_ $\otimes$, analogous to Cartesian product. For two experiments $X$ and $Y$, define $X \otimes Y = \{S \uparrow T : S \in X, T \in Y\}$.

Experiments and their two operations form a [semiring](https://en.wikipedia.org/wiki/Semiring). Union $\cap$ is a commutative monoid whose identity element is the empty Experiment $\varnothing$ (i.e., a set of no Specs at all). Product $\otimes$ is a non-commutative monoid with identity element $\{ \varnothing \}$ (i.e., an Experiment consisting of a single empty Spec). Note that the union identity $\varnothing$ is an absorbing element under the product operation: $X \otimes \varnothing = \varnothing \otimes X = \varnothing$ for any Experiment $X$.

### Conditional parameters

Informally, the "conditional" parameters in the v0.3 schema "filter" for parts of the Experiment and add new parameters in those situations.

Formally, conditional parameters require partitioning an Experiment into two parts. Each conditional parameter Spec $P$ is associated with a subset $Z$ of Specs in the experiment $X$. Adding a conditional parameter means taking the product of $P$ with this subset of $X$, keeping the other subsets of $X$ unchanged:

$$
(Z \otimes P) \cup (X \setminus Z)
$$

In the v0.3 schema, the subset $Z$ are those Specs that "match" some spec $M$:

$$
z \in Z \iff z \uparrow M = z
$$

In other words, $Z$ consists of those Specs that have that same name-value pairs that are in $M$.

In principle, the subset $Z$ could be defined by any predicate function, not just "matching."
