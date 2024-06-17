import random
import polars as pl


def replicated(
    func,
    n_replicates_key="n_replicates",
    seed_key="seed",
    replicate_var="replicate",
    replicate_type=pl.Int64,
):
    def replicated_func(param_set, *args, **kwargs):
        assert isinstance(param_set, dict)
        assert n_replicates_key in param_set
        assert seed_key in param_set

        # remove replicate-related keywords
        norep_param_set = {
            key: value
            for key, value in param_set.items()
            if key not in [n_replicates_key, seed_key]
        }

        random.seed(param_set[seed_key])

        return pl.concat(
            [
                (
                    func(norep_param_set, *args, **kwargs).with_columns(
                        pl.lit(i, dtype=replicate_type).alias(replicate_var)
                    )
                )
                for i in range(param_set[n_replicates_key])
            ]
        )

    return replicated_func
