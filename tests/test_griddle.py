from griddler.griddle import parse
import yaml


def test_baseline_only():
    griddle = """
    baseline_parameters:
      R0: 1.5
      gamma: 2.0
    """

    parameter_sets = parse(yaml.safe_load(griddle))
    assert parameter_sets == [{"R0": 1.5, "gamma": 2.0}]
