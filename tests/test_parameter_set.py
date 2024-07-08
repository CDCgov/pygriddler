from griddler import ParameterSet
import pytest


def test_validate_keys():
    """Keys must be strings"""
    with pytest.raises(ValueError, match="key"):
        ParameterSet({1: 2})


def test_validate_values_no_dict():
    """Value can't be a dict"""
    with pytest.raises(ValueError, match="invalid type"):
        ParameterSet({"param": {"sub_param": "value"}})


def test_validate_values_list_ok():
    """Value can be a list of things"""
    ParameterSet({"param_name": [1, 2.0, "foo", ["bar", "biz"]]})


def test_validate_values_tuple_ok():
    """Value can be a tuple of things"""
    ParameterSet({"param_name": (1, 2.0, "foo", ("bar", "biz"))})


def test_stable_hash():
    assert (
        ParameterSet({"gamma": 1.0, "beta": 2.0}).stable_hash()
        == "2d220d93aff966ac7c50"  # pragma: allowlist secret
    )


def test_stable_hash_sort_keys():
    """Hash should not depend on order"""
    ps1 = ParameterSet({"gamma": 1.0, "beta": 2.0})
    ps2 = ParameterSet({"beta": 2.0, "gamma": 1.0})
    assert ps1.stable_hash() == ps2.stable_hash()
