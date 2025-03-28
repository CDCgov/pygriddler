import pytest
import yaml

import griddler.griddle

# from griddler.griddle import _match_ps_nest, parse, read, read_to_json


def test_get_param_order_fail_not_dag_minimal():
    params = {
        "A": {"fix": "a", "if": {"B": "b"}},
        "B": {"fix": "b", "if": {"A": "a"}},
    }
    with pytest.raises(RuntimeError, match="The `if` conditions form a cycle"):
        griddler.griddle._get_param_order(params)


def test_get_param_order_simple():
    # B depends on A, so A should come first
    params = {
        "A": {"fix": "a"},
        "B": {"fix": "b", "if": {"A": "a"}},
    }
    assert griddler.griddle._get_param_order(params) == ["A", "B"]


def test_get_param_order_multiple():
    # B depends on A, so A should come first
    # C isn't part of the DAG, so it can come in any place
    params = {
        "A": {"fix": "a"},
        "B": {"fix": "b", "if": {"A": "a"}},
        "C": {"fix": "c"},
    }
    order = griddler.griddle._get_param_order(params)

    assert set(order) == {"A", "B", "C"}
    assert order.index("A") < order.index("B")


def test_baseline_only():
    raise NotImplementedError
    griddle = yaml.safe_load("""
    baseline_parameters:
      R0: 1.5
      gamma: 2.0
    """)

    parameter_sets = parse(griddle)
    assert parameter_sets == [{"R0": 1.5, "gamma": 2.0}]


def test_grid_only():
    raise NotImplementedError
    griddle = yaml.safe_load("""
    grid_parameters:
      R0: [1.0, 2.0]
      gamma: [1.0, 2.0]
    """)
    parameter_sets = parse(griddle)
    assert parameter_sets == [
        {"R0": 1.0, "gamma": 1.0},
        {"R0": 1.0, "gamma": 2.0},
        {"R0": 2.0, "gamma": 1.0},
        {"R0": 2.0, "gamma": 2.0},
    ]


def test_match_nest():
    raise NotImplementedError
    assert _match_ps_nest(
        parameter_set={"scenario": "optimistic"},
        nests=[
            {"scenario": "optimistic", "R0": 0.5},
            {"scenario": "pessimistic", "R0": 1.5},
        ],
    ) == {"scenario": "optimistic", "R0": 0.5}


def test_baseline_grid_nested():
    raise NotImplementedError
    griddle = yaml.safe_load("""
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

    parameter_sets = parse(griddle)
    assert parameter_sets == [
        {"scenario": "baseline", "R0": 1.0},
        {"scenario": "optimistic", "R0": 0.5},
        {"scenario": "pessimistic", "R0": 2.0},
    ]


def test_multiple_grid_nested():
    raise NotImplementedError
    parameter_sets = read("tests/fixtures/test_griddle_test_multiple_grid_nested.yaml")

    assert parameter_sets == [
        {"scenario": "baseline", "R0": 1.0, "gamma": 0.1},
        {"scenario": "baseline", "R0": 1.0, "gamma": 0.2},
        {"scenario": "optimistic", "R0": 0.5, "gamma": 0.1},
        {"scenario": "optimistic", "R0": 0.5, "gamma": 0.2},
        {"scenario": "pessimistic", "R0": 2.0, "gamma": 0.1},
        {"scenario": "pessimistic", "R0": 2.0, "gamma": 0.2},
    ]


def test_nested_dicts():
    raise NotImplementedError
    griddle = yaml.safe_load("""
    baseline_parameters:
      random_numbers:
        distribution: gamma
        shape: 1.0
        scale: 0.5
    """)

    parameter_sets = parse(griddle)
    assert parameter_sets == [griddle["baseline_parameters"]]


def test_read_to_json():
    raise NotImplementedError
    yaml_path = "tests/fixtures/test_griddle_test_multiple_grid_nested.yaml"

    with open("tests/fixtures/test_griddle_test_multiple_grid_nested.json") as f:
        json_text = f.read()

    assert read_to_json(yaml_path) + "\n" == json_text
