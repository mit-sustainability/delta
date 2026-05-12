import pytest
from dagster import Output

from cockpit.css.assets.raw import css_datahub_source
from cockpit.shared.resources import WarehouseTable


class _FakeDataHub:
    def get_project_id(self, name):
        return "fake-project-id"

    def search_files_from_project(self, project_id, term, tags=None, **kw):
        return ["https://fake-url/file.csv"]


class _FakeDataHubNoProject:
    def get_project_id(self, name):
        return None

    def search_files_from_project(self, project_id, term, tags=None, **kw):
        return []


class _FakeDataHubNoFiles:
    def get_project_id(self, name):
        return "fake-project-id"

    def search_files_from_project(self, project_id, term, tags=None, **kw):
        return []


class _FakeResponse:
    text = "col_a,col_b\nalpha,1\nbeta,2\ngamma,3"

    def raise_for_status(self):
        pass


def test_css_datahub_source_output(monkeypatch):
    monkeypatch.setattr(
        "cockpit.css.assets.raw.requests.get",
        lambda url, timeout: _FakeResponse(),
    )

    result = css_datahub_source(context=None, datahub=_FakeDataHub())

    assert isinstance(result, Output)
    assert isinstance(result.value, WarehouseTable)
    assert result.metadata["row_count"].value == 3
    assert result.value.columns == ("col_a", "col_b")


def test_css_datahub_source_missing_project_raises():
    with pytest.raises(RuntimeError, match="not found"):
        css_datahub_source(context=None, datahub=_FakeDataHubNoProject())


def test_css_datahub_source_missing_files_raises():
    with pytest.raises(RuntimeError, match="No files"):
        css_datahub_source(context=None, datahub=_FakeDataHubNoFiles())
