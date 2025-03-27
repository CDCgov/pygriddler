import json

import jsonschema
import jsonschema.exceptions
import pytest

with open("griddler/schema.json") as f:
    schema = json.load(f)


def test_fix_canonical():
    """Fixed parameter with canonical form"""
    jsonschema.validate([{"name": "R0", "type": "fix", "value": 1.0}], schema)


def test_fix_canonical_multiple():
    """Multiple fixed parameters with canonical form"""
    jsonschema.validate(
        [
            {"name": "R0", "type": "fix", "value": 1.0},
            {"name": "gamma", "type": "fix", "value": 2.0},
        ],
        schema,
    )


def test_fix_short_one():
    """Fixed parameter with short form"""
    jsonschema.validate([{"R0": 1.0}], schema)


def test_fix_short_fail_multiple_properties():
    """Malformed: fixed parameter with short form"""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate([{"R0": 1.0, "gamma": 2.0}], schema)


def test_vary_canonical_one():
    """Grid dimension with one parameter in canonical form"""
    jsonschema.validate(
        [{"type": "vary", "values": [{"name": "R0", "values": [1.0, 2.0]}]}],
        schema,
    )


def test_vary_canonical_multiple():
    """Grid dimension with multiple parameters in canonical form"""
    jsonschema.validate(
        [
            {
                "type": "vary",
                "values": [
                    {"name": "R0", "values": [1.0, 2.0]},
                    {"name": "gamma", "values": [2.0, 3.0]},
                ],
            }
        ],
        schema,
    )


def test_vary_short_one():
    """Grid dimension with one parameter in short form"""
    jsonschema.validate([{"R0": {"vary": [1.0, 2.0]}}], schema)


def test_vary_short_multiple():
    """Grid dimension with multiple parameters in short form"""
    jsonschema.validate(
        [{"type": "vary", "values": {"R0": [1.0, 2.0], "gamma": [2.0, 3.0]}}], schema
    )


def test_conditioned_fixed():
    """Conditioned fixed parameter in canonical form"""
    jsonschema.validate(
        [{"name": "R0", "type": "fix", "value": 1.0, "if": {"gamma": 2.0}}],
        schema,
    )


def test_conditioned_fixed_multiple_conditions():
    """Conditioned fixed parameter in canonical form with multiple conditions"""
    jsonschema.validate(
        [
            {
                "name": "R0",
                "type": "fix",
                "value": 1.0,
                "if": {"gamma": 2.0, "beta": 3.0},
            }
        ],
        schema,
    )


def test_conditioned_vary_canonical():
    """Conditioned grid dimension in canonical_form"""
    jsonschema.validate(
        [
            {
                "type": "vary",
                "values": [
                    {"name": "R0", "values": [1.0, 2.0]},
                    {"name": "gamma", "values": [2.0, 3.0]},
                ],
                "if": {"R0": 1.0},
            }
        ],
        schema,
    )


def test_conditioned_vary_short():
    """Conditioned grid dimension in short form"""
    jsonschema.validate(
        [
            {
                "type": "vary",
                "values": {"R0": [1.0, 2.0], "gamma": [2.0, 3.0]},
                "if": {"R0": 1.0},
            }
        ],
        schema,
    )
