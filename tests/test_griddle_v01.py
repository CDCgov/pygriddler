import pytest
import yaml

from griddler import parse
from griddler.schemas.v01 import _get_match, _is_match


def test_baseline_only():
    griddle = yaml.safe_load("""
    schema: v0.1
    baseline_parameters:
      R0: 1.5
      gamma: 2.0
    """)

    assert parse(griddle).to_dicts() == [{"R0": 1.5, "gamma": 2.0}]


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
    nests = [{"scenario": "optimistic", "R0": 0.5}]

    assert _get_match(param_set={"scenario": "optimistic"}, nests=nests) == 0

    assert (
        _get_match(param_set={"scenario": "pessimistic", "R0": 1.5}, nests=nests)
        is None
    )


def test_match_nest_multiple_matches():
    with pytest.raises(RuntimeError, match="matches multiple of"):
        _get_match(
            param_set={"scenario": "optimistic", "R0": 0.5},
            nests=[
                {"scenario": "optimistic", "gamma": 2.0},
                {"scenario": "pessimistic", "R0": 0.5},
            ],
        )


def test_is_match():
    assert _is_match({"a": 1, "b": 2}, {"a": 1, "c": 3}) is True
    assert _is_match({"a": 1, "b": 2}, {"a": 2, "c": 3}) is False
    assert _is_match({}, {"a": 1}) is False


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


def test_multiple_grid_nested():
    griddle = yaml.safe_load("""
    schema: v0.1

    baseline_parameters:
      R0: 1.0

    grid_parameters:
      scenario: [baseline, optimistic, pessimistic]
      gamma: [0.1, 0.2]

    nested_parameters:
      - scenario: optimistic
        R0: 0.5
      - scenario: pessimistic
        R0: 2.0
    """)

    parameter_sets = parse(griddle).to_dicts()
    assert parameter_sets == [
        {"scenario": "baseline", "R0": 1.0, "gamma": 0.1},
        {"scenario": "baseline", "R0": 1.0, "gamma": 0.2},
        {"scenario": "optimistic", "R0": 0.5, "gamma": 0.1},
        {"scenario": "optimistic", "R0": 0.5, "gamma": 0.2},
        {"scenario": "pessimistic", "R0": 2.0, "gamma": 0.1},
        {"scenario": "pessimistic", "R0": 2.0, "gamma": 0.2},
    ]


def test_unmatched_nests():
    griddle = yaml.safe_load("""
    schema: v0.1

    grid_parameters:
      scenario: [baseline, optimistic]

    nested_parameters:
      - scenario: pessimistic
        R0: 1.5
    """)

    with pytest.raises(RuntimeError, match="do not match any parameter sets"):
        parse(griddle)
