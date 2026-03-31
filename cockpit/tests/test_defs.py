from dagster import Definitions

from cockpit import defs


def test_dagster_definitions():
    assert isinstance(defs, Definitions)
