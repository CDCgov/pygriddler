import pytest

import griddler.griddle


# from griddler.griddle import _match_ps_nest, parse, read, read_to_json
def assert_list_setequal(a, b):
    """Assert that two lists have the same items, potentially in different order."""
    assert len(a) == len(b)
    for x in a:
        assert x in b, f"{x} not in {b}"

    for x in b:
        assert x in a, f"{x} not in {a}"


class TestParamOrder:
    def test_fail_not_dag_minimal(self):
        params = {
            "A": {"fix": "a", "if": {"B": "b"}},
            "B": {"fix": "b", "if": {"A": "a"}},
        }
        with pytest.raises(RuntimeError, match="The `if` conditions form a cycle"):
            griddler.griddle._get_param_order(params)

    def test_simple(self):
        # B depends on A, so A should come first
        params = {
            "A": {"fix": "a"},
            "B": {"fix": "b", "if": {"A": "a"}},
        }
        assert griddler.griddle._get_param_order(params) == ["A", "B"]

    def test_multiple(self):
        # B depends on A, so A should come first
        # C isn't part of the DAG, so it can come in any place
        params = {
            "A": {"fix": "a"},
            "B": {"fix": "b", "if": {"A": "a"}},
            "C": {"fix": "c"},
        }
        order = griddler.griddle._get_param_order(params)

        assert set(order) == {"A", "B", "C"}
        assert order.index("A") < order.index("B")


class TestValidateNames:
    def test_simple(self):
        raise NotImplementedError


class TestToCanonicalForm:
    def test_simple(self):
        raise NotImplementedError


class TestEvalCondition:
    def test_simple(self):
        raise NotImplementedError


class TestConditionDependsOn:
    def test_simple(self):
        raise NotImplementedError


class TestParse:
    def test_minimal(self):
        griddle = {"version": "v0.3", "parameters": {}}
        parameter_sets = griddler.griddle.parse(griddle)
        assert parameter_sets == [{}]

    def test_fixed_only(self):
        griddle = {"version": "v0.3", "parameters": {"R0": {"fix": 1.5}}}
        parameter_sets = griddler.griddle.parse(griddle)
        assert parameter_sets == [{"R0": 1.5}]

    def test_vary_one_canonical_one_value(self):
        params = {"my_bundle": {"vary": {"R0": [1.0]}}}
        parameter_sets = griddler.griddle._parse_params(params)
        assert parameter_sets == [{"R0": 1.0}]

    def test_vary_one_canonical(self):
        params = {"my_bundle": {"vary": {"R0": [1.0, 2.0]}}}
        parameter_sets = griddler.griddle._parse_params(params)
        assert_list_setequal(parameter_sets, [{"R0": 1.0}, {"R0": 2.0}])

    def test_vary_one_short(self):
        params = {"R0": {"vary": [1.0, 2.0]}}
        parameter_sets = griddler.griddle._parse_params(params)
        assert_list_setequal(
            parameter_sets,
            [
                {"R0": 1.0},
                {"R0": 2.0},
            ],
        )

    def test_2x2_grid(self):
        params = {"R0": {"vary": [1.0, 2.0]}, "gamma": {"vary": [1.0, 2.0]}}
        parameter_sets = griddler.griddle._parse_params(params)
        assert_list_setequal(
            parameter_sets,
            [
                {"R0": 1.0, "gamma": 1.0},
                {"R0": 1.0, "gamma": 2.0},
                {"R0": 2.0, "gamma": 1.0},
                {"R0": 2.0, "gamma": 2.0},
            ],
        )

    def test_bundle(self):
        params = {
            "R0": {"fix": 1.0},
            "scenario_bundle": {
                "vary": {"scenario": ["bad", "good"], "gamma": [1.0, 2.0]}
            },
        }
        parameter_sets = griddler.griddle._parse_params(params)
        assert_list_setequal(
            parameter_sets,
            [
                {"R0": 1.0, "scenario": "bad", "gamma": 1.0},
                {"R0": 1.0, "scenario": "good", "gamma": 2.0},
            ],
        )

    def test_vary_one_vary_bundle(self):
        params = {
            "gamma": {"vary": [0.1, 0.2]},
            "scenario": {"vary": {"R0": [1.0, 2.0], "theta": [1.0, 2.0]}},
        }
        parameter_sets = griddler.griddle._parse_params(params)

        expected = [
            {"gamma": 0.1, "R0": 1.0, "theta": 1.0},
            {"gamma": 0.1, "R0": 2.0, "theta": 2.0},
            {"gamma": 0.2, "R0": 1.0, "theta": 1.0},
            {"gamma": 0.2, "R0": 2.0, "theta": 2.0},
        ]

        assert_list_setequal(parameter_sets, expected)

    def test_if_trivial(self):
        params = {"x": {"fix": "X", "if": True}}
        parameter_sets = griddler.griddle._parse_params(params)
        assert parameter_sets == [{"x": "X"}]

    def test_if_simple(self):
        params = {"x": {"fix": "X"}, "y": {"fix": "Y", "if": {"equals": {"x": "X"}}}}
        parameter_sets = griddler.griddle._parse_params(params)
        assert parameter_sets == [{"x": "X", "y": "Y"}]
