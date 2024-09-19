from griddler.griddle import parse, _match_nest
import yaml


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
    assert (
        _match_nest(
            nest={"scenario": "optimistic", "R0": 0.5},
            parameter_sets=[{"scenario": "optimistic"}, {"scenario": "pessimistic"}],
        )
        == 0
    )


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
