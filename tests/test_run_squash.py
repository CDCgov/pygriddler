import polars as pl
import polars.testing

from griddler import run_squash


def test_run_squash_simple():
    def func(parameter_set):
        """
        Return a DataFrame with a single column `output`, which has the `word` duplicated `n_words`
        times (e.g., `foofoo` for word "foo" and 2 times) over `n_rows` rows
        """
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
        add_hash=False,
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


def test_run_squash_hash():
    def func(ps) -> pl.DataFrame:
        return pl.DataFrame({"x_plus_y": ps["x"] + ps["y"]})

    parameter_sets = [{"x": 1, "y": 1}, {"x": 10, "y": 2}]

    output = run_squash(func, parameter_sets, add_parameters=False, add_hash=True)

    assert set(output.columns) == {"x_plus_y", "hash"}


def test_run_squash_some_parameters():
    def func(ps) -> pl.DataFrame:
        return pl.DataFrame({"x_plus_y": ps["x"] + ps["y"]})

    parameter_sets = [{"x": 1, "y": 1}, {"x": 10, "y": 2}]

    output = run_squash(func, parameter_sets, parameter_columns=["x"], add_hash=False)

    expected = pl.DataFrame({"x_plus_y": [2, 12], "x": [1, 10]})

    polars.testing.assert_frame_equal(output, expected, check_dtypes=False)


def test_run_squash_nested_dict():
    def func(ps) -> pl.DataFrame:
        return pl.DataFrame({"x_plus_y": ps["numbers"]["x"] + ps["numbers"]["y"]})

    parameter_sets = [{"numbers": {"x": 1, "y": 2}}]
    output = run_squash(func, parameter_sets, add_hash=False)
    expected = pl.DataFrame({"x_plus_y": 3, "numbers": pl.struct(x=1, y=2, eager=True)})
    polars.testing.assert_frame_equal(output, expected, check_dtypes=False)
