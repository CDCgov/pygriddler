import jsonschema
import jsonschema.exceptions
import pytest

import griddler

schema = griddler.Griddle.load_schema()


def validate_griddle(x: dict) -> None:
    """Validate an entire griddle"""
    jsonschema.Draft202012Validator(schema).validate(x)


def validate_experiment(x: dict | list) -> None:
    """Validate the experiment inside a griddle"""
    validate_griddle({"version": "my_version", "experiment": x})


def test_v0_2_griddle_fails():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        validate_griddle({"experiment": [{"R0": 1.0}]})


def test_griddle_minimal():
    """Minimal griddle"""
    validate_griddle({"version": "my_version", "experiment": []})


def test_griddle_one_spec():
    """Griddle with one fixed parameter"""
    validate_griddle({"version": "my_version", "experiment": [{"R0": 1.5}]})


def test_experiment_two_spec():
    """Experiment with two specs"""
    validate_experiment([{"R0": 1.5}, {"R0": 2.5}])


def test_experiment_union():
    """Experiment with union of two specs"""
    validate_experiment({"union": [[{"R0": 1.5}], [{"gamma": 1.0}]]})


def test_experiment_product():
    """Experiment with product of two specs"""
    validate_experiment(
        {"product": [[{"R0": 1.5}, {"R0": 2.5}], [{"gamma": 1.0}, {"gamma": 2.0}]]}
    )


def test_experiment_product_union():
    """Experiment that is a product of a union of two experiments"""
    validate_experiment(
        {
            "product": [
                [{"R0": 1.5}],
                {"union": [[{"method": "brent"}], [{"lower": 0.0}]]},
            ]
        }
    )
