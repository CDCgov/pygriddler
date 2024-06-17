import polars as pl
import polars.testing
from griddler import run_squash


def test_run_squash_simple():
    def func(parameter_set):
        return pl.DataFrame(
            {
                "output": [
                    parameter_set["word"] * parameter_set["n_words"]
                    for i in range(parameter_set["n_rows"])
                ]
            }
        )

    output = run_squash(
        func,
        [
            {"word": "foo", "n_words": 2, "n_rows": 1},
            {"word": "bar", "n_words": 1, "n_rows": 2},
        ],
    )

    polars.testing.assert_frame_equal(
        output,
        pl.DataFrame(
            {
                "word": ["foo", "bar", "bar"],
                "n_words": [2, 1, 1],
                "n_rows": [1, 2, 2],
                "output": ["foofoo", "bar", "bar"],
            }
        ),
        check_column_order=False,
        check_dtypes=False,
    )
