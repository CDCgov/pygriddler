import contextlib
import io

import pytest

import griddler.__main__


def test_cli_help():
    """Run the cli with --help argument"""
    # we should get an exit with status 0
    with pytest.raises(SystemExit):
        # we should also get a help message
        with contextlib.redirect_stdout(io.StringIO()) as f:
            griddler.__main__.main(["--help"])

    result = f.getvalue()

    # Check that the output contains expected strings
    assert "usage" in result
