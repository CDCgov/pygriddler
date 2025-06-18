import yaml

from griddler import parse
from griddler.schemas.v01 import _match_nest


def test_grid_only():
    griddle = yaml.safe_load("""
    schema: v0.1
    grid_parameters:
      R0: [1.0, 2.0]
      gamma: [1.0, 2.0]
    """)
    assert parse(griddle).to_dicts() == [
        {"R0": 1.0, "gamma": 1.0},
        {"R0": 1.0, "gamma": 2.0},
        {"R0": 2.0, "gamma": 1.0},
        {"R0": 2.0, "gamma": 2.0},
    ]


def test_match_nest():
    assert (
        _match_nest(
            nest={"scenario": "optimistic", "R0": 0.5},
            param_sets=[{"scenario": "optimistic"}, {"scenario": "pessimistic"}],
        )
        == 0
    )


def test_baseline_grid_nested():
    griddle = yaml.safe_load("""
    schema: v0.1

    baseline_parameters:
      R0: 1.0

    grid_parameters:
      scenario: [baseline, optimistic, pessimistic]

    nested_parameters:
      - scenario: optimistic
        R0: 0.5
      - scenario: pessimistic
        R0: 2.0
    """)

    assert parse(griddle).to_dicts() == [
        {"scenario": "baseline", "R0": 1.0},
        {"scenario": "optimistic", "R0": 0.5},
        {"scenario": "pessimistic", "R0": 2.0},
    ]
