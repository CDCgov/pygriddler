from typing import Any

import pytest
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


def test_vary():
    assert text_to_dicts("""
    schema: v0.3
    parameters:
      R0: {vary: [1.5, 2.0]}
      gamma: {vary: [0.3, 0.4]}
    """) == [
        {"R0": 1.5, "gamma": 0.3},
        {"R0": 1.5, "gamma": 0.4},
        {"R0": 2.0, "gamma": 0.3},
        {"R0": 2.0, "gamma": 0.4},
    ]


def test_bundle():
    assert text_to_dicts("""
    schema: v0.3
    parameters:
      scenario:
        R0: [low, high]
        gamma: [low, high]
    """) == [{"R0": "low", "gamma": "low"}, {"R0": "high", "gamma": "high"}]


def test_conditional():
    assert text_to_dicts("""
    schema: v0.3
    parameters:
      method: {vary: [newton, brent]}
      start_point:
        if: {equals: {method: newton}}
        vary: [0.25, 0.50, 0.75]
      bounds:
        if: {equals: {method: brent}}
        fix: [0.0, 1.0]
    """) == [
        {"method": "brent", "bounds": [0.0, 1.0]},
        {"method": "newton", "start_point": 0.25},
        {"method": "newton", "start_point": 0.50},
        {"method": "newton", "start_point": 0.75},
    ]


def test_comment():
    assert text_to_dicts("""
    schema: v0.3
    parameters:
      R0: {fix: 1.0, comment: "This is a comment"}
    """) == [{"R0": 1.0}]


def test_reserved_words():
    # Test that reserved words in the bundle are not allowed
    with pytest.raises(RuntimeError, match="vary"):
        text_to_dicts("""
        schema: v0.3
        parameters:
          R0: {fix: 1.0, vary: ["bar"]}
        """)

    with pytest.raises(RuntimeError, match="my_bad_key"):
        text_to_dicts("""
        schema: v0.3
        parameters:
          R0: {vary: [1.0], my_bad_key: ["bar"]}
        """)

    with pytest.raises(RuntimeError, match="comment"):
        text_to_dicts("""
        schema: v0.3
        parameters:
          scenario:
            R0: [1.0, 1.5]
            comment: []
        """)
