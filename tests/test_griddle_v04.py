from typing import List

import jsonschema
import jsonschema.exceptions
import pytest

from griddler import parse
from griddler.schemas.v04 import load_schema


class TestParse:
    @staticmethod
    def assert_list_setequal(a, b):
        """Assert that two lists have the same items, potentially in different order."""
        assert len(a) == len(b)
        for x in a:
            assert x in b, f"{x} not in {b}"

        for x in b:
            assert x in a, f"{x} not in {a}"

    @staticmethod
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
        assert self.parse_experiment(expt) == expt

    def test_experiment_union(self):
        expt = {"union": [[{"R0": 1.5}], [{"gamma": 1.0}]]}
        assert self.parse_experiment(expt) == [{"R0": 1.5}, {"gamma": 1.0}]

    def test_experiment_product(self):
        expt = {
            "product": [[{"R0": 1.5}, {"R0": 2.5}], [{"gamma": 1.0}, {"gamma": 2.0}]]
        }
        assert self.parse_experiment(expt) == [
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
        assert self.parse_experiment(expt) == [
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
        assert self.parse_experiment(expt) == [
            {"R0": 1.5, "method": "brent", "lower_bound": 0.0, "upper_bound": 1.0},
            {"R0": 1.5, "method": "newton", "start_point": 0.25},
            {"R0": 1.5, "method": "newton", "start_point": 0.50},
            {"R0": 1.5, "method": "newton", "start_point": 0.75},
        ]


class TestSchema:
    schema = load_schema()

    @classmethod
    def validate_griddle(cls, x: dict) -> None:
        """Validate an entire griddle"""
        jsonschema.Draft202012Validator(cls.schema).validate(x)

    @classmethod
    def validate_experiment(cls, x: dict | list) -> None:
        """Validate the experiment inside a griddle"""
        cls.validate_griddle({"schema": "my_schema", "experiment": x})

    def test_v0_2_griddle_fails(self):
        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.validate_griddle({"experiment": [{"R0": 1.0}]})

    def test_griddle_minimal(self):
        """Minimal griddle"""
        self.validate_griddle({"schema": "my_schema", "experiment": []})

    def test_griddle_one_spec(self):
        """Griddle with one fixed parameter"""
        self.validate_griddle({"schema": "my_schema", "experiment": [{"R0": 1.5}]})

    def test_experiment_two_spec(self):
        """Experiment with two specs"""
        self.validate_experiment([{"R0": 1.5}, {"R0": 2.5}])

    def test_experiment_union(self):
        """Experiment with union of two specs"""
        self.validate_experiment({"union": [[{"R0": 1.5}], [{"gamma": 1.0}]]})

    def test_experiment_product(self):
        """Experiment with product of two specs"""
        self.validate_experiment(
            {"product": [[{"R0": 1.5}, {"R0": 2.5}], [{"gamma": 1.0}, {"gamma": 2.0}]]}
        )

    def test_experiment_product_union(self):
        """Experiment that is a product of a union of two experiments"""
        self.validate_experiment(
            {
                "product": [
                    [{"R0": 1.5}],
                    {"union": [[{"method": "brent"}], [{"lower": 0.0}]]},
                ]
            }
        )
