import jsonschema
import jsonschema.exceptions
import pytest

import griddler.griddle

schema = griddler.griddle.load_schema()


def validate_griddle(x: dict) -> None:
    """Validate an entire griddle"""
    jsonschema.Draft202012Validator(schema).validate(x)


def validate_parameters(x: dict) -> None:
    """Validate the parameters dictionary inside a griddle"""
    validate_griddle({"version": "my_version", "parameters": x})


def test_v0_2_griddle_fails():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        validate_griddle({"baseline_parameters": {"R0": 1.5, "gamma": 2.0}})


def test_griddle_minimal():
    """Minimal griddle"""
    validate_griddle({"version": "my_version", "parameters": {}})


def test_griddle_one():
    """Griddle with one dimension"""
    validate_griddle({"version": "my_version", "parameters": {"R0": {"fix": 1.5}}})


def test_fix_scalar():
    """Fixed parameter with canonical form"""
    validate_parameters({"R0": {"fix": 1.0}})


def test_fix_array():
    """Fixed parameter with array form"""
    validate_parameters({"R0": {"fix": [1.0, 2.0]}})


def test_fix_multiple():
    """Multiple fixed parameters"""
    validate_parameters(
        {"R0": {"fix": 1.0}, "gamma": {"fix": 2.0}, "beta": {"fix": 3.0}}
    )


def test_fixed_fail_on_bad_field():
    """Fixed parameter with bad field"""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        validate_parameters({"R0": {"fix": 1.0, "bad_field": True}})


def test_vary_one():
    """Varying bundle with one parameter"""
    validate_parameters({"R0_bundle": {"vary": {"R0": [1.0, 2.0]}}})


def test_vary_fail_on_bad_field():
    """Varying bundle with one parameter with bad field"""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        validate_parameters(
            {"R0_bundle": {"vary": {"R0": [1.0, 2.0]}, "bad_field": True}}
        )


def test_vary_multiple():
    """Varying bundle with multiple parameters"""
    validate_parameters(
        {"my_bundle": {"vary": {"R0": [1.0, 2.0], "gamma": [2.0, 3.0]}}}
    )


def test_vary_one_short():
    """Varying bundle with one parameter, in short form"""
    validate_parameters({"R0": {"vary": [1.0, 2.0]}})


def test_conditioned_fixed():
    """Conditioned fixed parameter"""
    validate_parameters({"R0": {"fix": 1.0, "if": {"equals": {"gamma": 2.0}}}})


def test_conditioned_vary():
    """Conditioned varying bundle in canonical_form"""
    validate_parameters(
        {
            "my_bundle": {
                "vary": {"R0": [1.0, 2.0], "gamma": [2.0, 3.0]},
                "if": {"equals": {"R0": 1.0}},
            }
        }
    )


def test_conditioned_vary_short():
    """Conditioned varying bundle, with one parameter in short form"""
    validate_parameters({"R0": {"vary": [1.0, 2.0], "if": {"equals": {"gamma": 2.0}}}})


def test_fixed_comment():
    """Fixed parameter with comment"""
    validate_parameters({"R0": {"fix": 1.0, "comment": "This is a comment"}})
