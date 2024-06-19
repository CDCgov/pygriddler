from griddler import ParameterSet

def test_to_tuple_simple():
    """Converts simple parameter sets to tuples"""
    ps = ParameterSet({"gamma": 1.0, "beta": 2.0})
    assert ps.to_tuple() == (("beta", 2.0), ("gamma", 1.0))

def test_to_tuple_nested():
    """Converts parameter sets with tuples"""
    ps = ParameterSet({"R0": 2.0, "introduction_times": (0.0, 1.1, 2.2)})
    assert ps.to_tuple() == (("R0", 2.0), ("introduction_times", (0.0, 1.1, 2.2)))

def test_can_hash():
    ps = ParameterSet({"gamma": 1.0, "beta": 2.0})
    assert ps.to_tuple() == (("beta", 2.0), ("gamma", 1.0))
    t = ps.to_tuple()
    assert hash(t) == 1234
    assert ps.hash() == 6011366373467269404
