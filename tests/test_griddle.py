import yaml

from griddler.griddle import _match_ps_nest, parse, read, read_to_json


def test_baseline_only():
    griddle = yaml.safe_load("""
    baseline_parameters:
      R0: 1.5
      gamma: 2.0
    """)

    parameter_sets = parse(griddle)
    assert parameter_sets == [{"R0": 1.5, "gamma": 2.0}]


def test_grid_only():
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
    assert _match_ps_nest(
        parameter_set={"scenario": "optimistic"},
        nests=[
            {"scenario": "optimistic", "R0": 0.5},
            {"scenario": "pessimistic", "R0": 1.5},
        ],
    ) == {"scenario": "optimistic", "R0": 0.5}


def test_baseline_grid_nested():
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
    yaml_path = "tests/fixtures/test_griddle_test_multiple_grid_nested.yaml"

    with open("tests/fixtures/test_griddle_test_multiple_grid_nested.json") as f:
        json_text = f.read()

    assert read_to_json(yaml_path) + "\n" == json_text
