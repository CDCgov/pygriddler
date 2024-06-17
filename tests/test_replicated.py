from griddler import replicated
import random
import polars as pl
import polars.testing


def test_simple_replicated():
    def func(parameter_set):
        return pl.DataFrame({"x": [round(random.uniform(0, 1), 2) for i in range(3)]})

    rep_func = replicated(func)
    output = rep_func({"seed": 42, "n_replicates": 2})
    expected = pl.DataFrame(
        {"replicate": [0, 0, 0, 1, 1, 1], "x": [0.64, 0.03, 0.28, 0.22, 0.74, 0.68]}
    )

    polars.testing.assert_frame_equal(output, expected, check_column_order=False)
