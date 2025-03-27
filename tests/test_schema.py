import json

import jsonschema
import jsonschema.exceptions
import pytest

with open("griddler/schema.json") as f:
    schema = json.load(f)


def validate_griddle(x):
    jsonschema.Draft202012Validator(schema).validate(x)


def validate_dimensions(x):
    validate_griddle({"version": "my_version", "dimensions": x})


def test_griddle_minimal():
    """Minimal griddle"""
    validate_griddle({"version": "my_version", "dimensions": []})


def test_griddle_one():
    """Griddle with one dimension"""
    validate_griddle({"version": "my_version", "dimensions": [{"R0": 1.5}]})


def test_fix_canonical():
    """Fixed parameter with canonical form"""
    validate_dimensions([{"name": "R0", "type": "fix", "value": 1.0}])


def test_fix_canonical_multiple():
    """Multiple fixed parameters with canonical form"""
    validate_dimensions(
        [
            {"name": "R0", "type": "fix", "value": 1.0},
            {"name": "gamma", "type": "fix", "value": 2.0},
        ]
    )


def test_fix_short_one():
    """Fixed parameter with short form"""
    validate_dimensions([{"R0": 1.0}])


def test_fix_short_fail_multiple_properties():
    """Malformed fixed parameter with short form"""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        validate_dimensions([{"R0": 1.0, "gamma": 2.0}])


def test_fix_short_fail_reserved_word():
    """Fixed parameter with short form, but with a keyword name"""
    for x in ["name", "type", "vary", "value", "values", "if", "comment"]:
        try:
            validate_dimensions([{x: 1.0}])
            raise RuntimeError(f"Should have failed with key '{x}'")
        except jsonschema.exceptions.ValidationError:
            pass


def test_vary_canonical_one():
    """Grid dimension with one parameter in canonical form"""
    validate_dimensions(
        [{"type": "vary", "values": [{"name": "R0", "values": [1.0, 2.0]}]}]
    )


def test_vary_canonical_multiple():
    """Grid dimension with multiple parameters in canonical form"""
    validate_dimensions(
        [
            {
                "type": "vary",
                "values": [
                    {"name": "R0", "values": [1.0, 2.0]},
                    {"name": "gamma", "values": [2.0, 3.0]},
                ],
            }
        ]
    )


def test_vary_short_one():
    """Grid dimension with one parameter in short form"""
    validate_dimensions([{"R0": {"vary": [1.0, 2.0]}}])


def test_vary_short_multiple():
    """Grid dimension with multiple parameters in short form"""
    validate_dimensions(
        [{"type": "vary", "values": {"R0": [1.0, 2.0], "gamma": [2.0, 3.0]}}]
    )


def test_conditioned_fixed():
    """Conditioned fixed parameter in canonical form"""
    validate_dimensions(
        [{"name": "R0", "type": "fix", "value": 1.0, "if": {"gamma": 2.0}}]
    )


def test_conditioned_fixed_multiple_conditions():
    """Conditioned fixed parameter in canonical form with multiple conditions"""
    validate_dimensions(
        [
            {
                "name": "R0",
                "type": "fix",
                "value": 1.0,
                "if": {"gamma": 2.0, "beta": 3.0},
            }
        ]
    )


def test_conditioned_vary_canonical():
    """Conditioned grid dimension in canonical_form"""
    validate_dimensions(
        [
            {
                "type": "vary",
                "values": [
                    {"name": "R0", "values": [1.0, 2.0]},
                    {"name": "gamma", "values": [2.0, 3.0]},
                ],
                "if": {"R0": 1.0},
            }
        ]
    )


def test_conditioned_vary_short():
    """Conditioned grid dimension in short form"""
    validate_dimensions(
        [
            {
                "type": "vary",
                "values": {"R0": [1.0, 2.0], "gamma": [2.0, 3.0]},
                "if": {"R0": 1.0},
            }
        ]
    )
