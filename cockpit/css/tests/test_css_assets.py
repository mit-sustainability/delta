from dagster import Definitions

from cockpit.css.defs import css_defs


def test_css_defs_is_definitions():
    assert isinstance(css_defs, Definitions)
