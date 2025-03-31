import pytest

from griddler import FixParam, Griddle, Param


def assert_list_setequal(a, b):
    """Assert that two lists have the same items, potentially in different order."""
    assert len(a) == len(b)
    for x in a:
        assert x in b, f"{x} not in {b}"

    for x in b:
        assert x in a, f"{x} not in {a}"


def params_from_json(params_dict):
    """Convert a dictionary of parameters into a list of Param objects."""
    return [Param.from_json(name, spec) for name, spec in params_dict.items()]


class TestParamOrder:
    def test_fail_not_dag_minimal(self):
        params = {
            "A": {"fix": "a", "if": {"equals": {"B": "b"}}},
            "B": {"fix": "b", "if": {"equals": {"A": "a"}}},
        }
        with pytest.raises(RuntimeError, match="The `if` conditions form a cycle"):
            Griddle._get_param_order(params_from_json(params))

    def test_simple(self):
        # B depends on A, so A should come first
        params = {
            "A": {"fix": "a"},
            "B": {"fix": "b", "if": {"equals": {"A": "a"}}},
        }
        assert Griddle._get_param_order(params_from_json(params)) == ["A", "B"]

    def test_multiple(self):
        # B depends on A, so A should come first
        # C isn't part of the DAG, so it can come in any place
        params = {
            "A": {"fix": "a"},
            "B": {"fix": "b", "if": {"equals": {"A": "a"}}},
            "C": {"fix": "c"},
        }
        order = Griddle._get_param_order(params_from_json(params))

        assert set(order) == {"A", "B", "C"}
        assert order.index("A") < order.index("B")


class TestValidateNames:
    def test_simple(self):
        params_dict = {"A": {"fix": "a"}, "B": {"vary": {"A": [1, 2]}}}
        params = params_from_json(params_dict)
        with pytest.raises(AssertionError, match=r"(?i)duplicate parameter name"):
            Griddle._validate_parameter_names(params)


class TestEvalCondition:
    def test_trivial(self):
        assert FixParam(name="x", value="x", if_=True).eval_condition({}) is True

    def test_trivial_with_value(self):
        assert (
            FixParam(name="x", value="x", if_=True).eval_condition({"y": "y"}) is True
        )

    def test_simple_equals(self):
        assert (
            FixParam(name="x", value="x", if_={"equals": {"y": "y"}}).eval_condition(
                {"y": "y"}
            )
            is True
        )

        assert (
            FixParam(name="x", value="x", if_={"equals": {"y": "y"}}).eval_condition(
                {"y": "z"}
            )
            is False
        )


class TestConditionDependsOn:
    def test_fixed_none(self):
        assert FixParam(name="x", value="x", if_=True).depends_on() == set()

    def test_fixed(self):
        assert FixParam(
            name="x", value="x", if_={"equals": {"y": "y"}}
        ).depends_on() == {"y"}


class TestParse:
    def test_minimal(self):
        griddle = {"version": "v0.3", "parameters": {}}
        parameter_sets = Griddle(griddle).parse()
        assert parameter_sets == [{}]

    def test_fixed_only(self):
        griddle = {"version": "v0.3", "parameters": {"R0": {"fix": 1.5}}}
        parameter_sets = Griddle(griddle).parse()
        assert parameter_sets == [{"R0": 1.5}]

    def test_vary_one_canonical_one_value(self):
        params = {"my_bundle": {"vary": {"R0": [1.0]}}}
        parameter_sets = Griddle._parse_params(params)
        assert parameter_sets == [{"R0": 1.0}]

    def test_vary_one_canonical(self):
        params = {"my_bundle": {"vary": {"R0": [1.0, 2.0]}}}
        parameter_sets = Griddle._parse_params(params)
        assert_list_setequal(parameter_sets, [{"R0": 1.0}, {"R0": 2.0}])

    def test_vary_one_short(self):
        params = {"R0": {"vary": [1.0, 2.0]}}
        parameter_sets = Griddle._parse_params(params)
        assert_list_setequal(
            parameter_sets,
            [
                {"R0": 1.0},
                {"R0": 2.0},
            ],
        )

    def test_2x2_grid(self):
        params = {"R0": {"vary": [1.0, 2.0]}, "gamma": {"vary": [1.0, 2.0]}}
        parameter_sets = Griddle._parse_params(params)
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
        parameter_sets = Griddle._parse_params(params)
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
        parameter_sets = Griddle._parse_params(params)

        expected = [
            {"gamma": 0.1, "R0": 1.0, "theta": 1.0},
            {"gamma": 0.1, "R0": 2.0, "theta": 2.0},
            {"gamma": 0.2, "R0": 1.0, "theta": 1.0},
            {"gamma": 0.2, "R0": 2.0, "theta": 2.0},
        ]

        assert_list_setequal(parameter_sets, expected)

    def test_if_trivial(self):
        params = {"x": {"fix": "X", "if": True}}
        parameter_sets = Griddle._parse_params(params)
        assert parameter_sets == [{"x": "X"}]

    def test_if_simple(self):
        params = {"x": {"fix": "X"}, "y": {"fix": "Y", "if": {"equals": {"x": "X"}}}}
        parameter_sets = Griddle._parse_params(params)
        assert parameter_sets == [{"x": "X", "y": "Y"}]

    def test_subgrid(self):
        params = {
            "state_and_capital": {
                "vary": {
                    "state": ["Virginia", "North Dakota"],
                    "capital": ["Richmond", "Pierre"],
                }
            },
            "beach_town": {
                "if": {"equals": {"state": "Virginia"}},
                "vary": ["Virginia Beach", "Chincoteague", "Colonial Beach"],
            },
        }
        parameter_sets = Griddle._parse_params(params)
        print(parameter_sets)
        expected = [
            {
                "state": "Virginia",
                "capital": "Richmond",
                "beach_town": "Virginia Beach",
            },
            {"state": "Virginia", "capital": "Richmond", "beach_town": "Chincoteague"},
            {
                "state": "Virginia",
                "capital": "Richmond",
                "beach_town": "Colonial Beach",
            },
            {"state": "North Dakota", "capital": "Pierre"},
        ]
        assert_list_setequal(parameter_sets, expected)

    def test_conditional_newton_example(self):
        params_dict = {
            "method": {"vary": ["newton", "brent"]},
            "start_point": {
                "if": {"equals": {"method": "newton"}},
                "vary": [0.25, 0.50, 0.75],
            },
            "bounds": {"if": {"equals": {"method": "brent"}}, "fix": [0.0, 1.0]},
        }
        parameter_sets = Griddle._parse_params(params_dict)
        expected = [
            {"method": "newton", "start_point": 0.25},
            {"method": "newton", "start_point": 0.5},
            {"method": "newton", "start_point": 0.75},
            {"method": "brent", "bounds": [0.0, 1.0]},
        ]
        assert_list_setequal(parameter_sets, expected)
