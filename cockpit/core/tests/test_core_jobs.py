from cockpit.core.defs import core_defs


def test_core_defs_has_no_jobs():
    assert not list(core_defs.jobs)
