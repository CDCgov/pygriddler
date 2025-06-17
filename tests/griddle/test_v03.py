from typing import Any

import yaml

from griddler import parse


def text_to_dicts(text: str) -> list[dict[str, Any]]:
    """Convert a YAML text to a list of dictionaries."""
    data = yaml.safe_load(text)
    return parse(data).to_dicts()


def test_simple():
    assert text_to_dicts("""
    schema: v0.3
    parameters:
      R0: {fix: 1.0}
    """) == [{"R0": 1.0}]
