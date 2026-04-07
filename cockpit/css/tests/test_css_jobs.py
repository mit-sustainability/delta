from cockpit.css.defs import css_defs


def test_css_defs_includes_job():
    assert {job.name for job in css_defs.jobs} == {"css_job"}
