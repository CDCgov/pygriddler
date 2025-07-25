__all__ = ["Experiment", "parse"]

import griddler.schemas.v01
import griddler.schemas.v03
import griddler.schemas.v04
from griddler.core import Experiment


def parse(griddle: dict) -> Experiment:
    """Parse a griddle into an Experiment."""
    assert isinstance(griddle, dict), "griddle must be a dictionary"
    assert "schema" in griddle, "griddle must have a schema"

    match griddle["schema"]:
        case "v0.1":
            return griddler.schemas.v01.parse(griddle)
        case "v0.3":
            return griddler.schemas.v03.parse(griddle)
        case "v0.4":
            return griddler.schemas.v04.parse(griddle)
        case _:
            raise RuntimeError(f"Unknown griddle schema: {griddle['schema']}")
