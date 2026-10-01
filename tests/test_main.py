import contextlib
import io

import pytest

import griddler.__main__
from griddler import parse


def test_cli_help():
    """Run the cli with --help argument"""
    # we should get an exit with status 0
    with pytest.raises(SystemExit), contextlib.redirect_stdout(io.StringIO()) as f:
        griddler.__main__.main(["--help"])

    result = f.getvalue()

    # Check that the output contains expected strings
    assert "usage" in result


def test_can_iter():
    """Test that the main function can be iterated over"""
    griddle = {"schema": "v0.4", "experiment": [{"R0": 1.5}, {"R0": 2.5}]}

    i = 0
    for _ in parse(griddle):
        i += 1

    assert i == 2
