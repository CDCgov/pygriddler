from typing import List

from griddler import parse


def assert_list_setequal(a, b):
    """Assert that two lists have the same items, potentially in different order."""
    assert len(a) == len(b)
    for x in a:
        assert x in b, f"{x} not in {b}"

    for x in b:
        assert x in a, f"{x} not in {a}"


def parse_experiment(x: dict | list) -> List[dict]:
    """Convenience function to avoid writing the schema every time."""
    griddle = {"schema": "v0.4", "experiment": x}
    return parse(griddle).to_dicts()


def test_minimal(self):
    griddle = {"schema": "v0.4", "experiment": []}
    assert parse(griddle).to_dicts() == []


def test_almost_minimal(self):
    griddle = {"schema": "v0.4", "experiment": [{}]}
    assert parse(griddle).to_dicts() == [{}]


def test_fixed_only(self):
    griddle = {"schema": "v0.4", "experiment": [{"R0": 1.5}]}
    assert parse(griddle).to_dicts() == [{"R0": 1.5}]


def test_simple_experiment(self):
    expt = [{"R0": 1.5}, {"R0": 2.5}]
    assert parse_experiment(expt) == expt


def test_experiment_union(self):
    expt = {"union": [[{"R0": 1.5}], [{"gamma": 1.0}]]}
    assert parse_experiment(expt) == [{"R0": 1.5}, {"gamma": 1.0}]


def test_experiment_product(self):
    expt = {"product": [[{"R0": 1.5}, {"R0": 2.5}], [{"gamma": 1.0}, {"gamma": 2.0}]]}
    assert parse_experiment(expt) == [
        {"R0": 1.5, "gamma": 1.0},
        {"R0": 1.5, "gamma": 2.0},
        {"R0": 2.5, "gamma": 1.0},
        {"R0": 2.5, "gamma": 2.0},
    ]


def test_nested1(self):
    expt = {
        "product": [
            [{"R0": 1.5}],
            {"union": [[{"method": "brent"}], [{"lower": 0.0}]]},
        ]
    }
    assert parse_experiment(expt) == [
        {"R0": 1.5, "method": "brent"},
        {"R0": 1.5, "lower": 0.0},
    ]


def test_nested2(self):
    expt = {
        "product": [
            [{"R0": 1.5}],
            {
                "union": [
                    [{"method": "brent", "lower_bound": 0.0, "upper_bound": 1.0}],
                    {
                        "product": [
                            [{"method": "newton"}],
                            [
                                {"start_point": 0.25},
                                {"start_point": 0.50},
                                {"start_point": 0.75},
                            ],
                        ]
                    },
                ]
            },
        ],
    }
    assert parse_experiment(expt) == [
        {"R0": 1.5, "method": "brent", "lower_bound": 0.0, "upper_bound": 1.0},
        {"R0": 1.5, "method": "newton", "start_point": 0.25},
        {"R0": 1.5, "method": "newton", "start_point": 0.50},
        {"R0": 1.5, "method": "newton", "start_point": 0.75},
    ]
