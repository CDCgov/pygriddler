import json

import jsonschema

with open("griddler/schema.json") as f:
    schema = json.load(f)


def test_fix_canonical():
    """Fixed parameter with canonical format"""
    jsonschema.validate([{"name": "R0", "type": "fix", "value": 1.0}], schema)


def test_fix_canonical_multiple():
    """Multiple fixed parameters with canonical format"""
    jsonschema.validate(
        [
            {"name": "R0", "type": "fix", "value": 1.0},
            {"name": "gamma", "type": "fix", "value": 2.0},
        ],
        schema,
    )


def test_fix_short_one():
    """Fixed parameter with short format"""
    jsonschema.validate([{"R0": 1.0}], schema)
