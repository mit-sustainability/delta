from cockpit.mitos.defs import mitos_defs


def test_mitos_defs_includes_job():
    assert {job.name for job in mitos_defs.jobs} == {"mitos_job"}
