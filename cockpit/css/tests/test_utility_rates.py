import pandas as pd
import pytest
from dagster import Output

from cockpit.css.assets.utility_rates import (
    assumed_rate,
    chilled_water_residuals,
    electricity_residuals,
    mthw_consumption_pi,
    steam_residuals,
)
from cockpit.shared.resources import WarehouseTable


class _FakeDataHub:
    def get_project_id(self, name):
        return "fake-project-id"

    def search_files_from_project(self, project_id, term, tags=None, **kw):
        return ["https://fake-url/file.xlsx"]


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


def _sequential_read_excel(*dfs):
    """Returns a pd.read_excel replacement yielding dfs in call order."""
    it = iter(dfs)

    def _fake(workbook, **kwargs):
        return next(it)

    return _fake


def test_electricity_residuals_outputs(monkeypatch):
    consumption_df = pd.DataFrame(
        {
            "Square feet": ["Bldg A", "Bldg B", "Total"],
            "Bldg #": [None, "102", None],
            "SAP": ["S1", "S2", "S3"],
            "ADJUSTED METERS": [100.0, 200.0, 300.0],
        }
    )
    production_df = pd.DataFrame({"item": ["Line 1", "Line 2"], "amount": [1000.0, 2000.0]})

    monkeypatch.setattr(pd, "ExcelFile", lambda url, engine: "fake_wb")
    monkeypatch.setattr(pd, "read_excel", _sequential_read_excel(consumption_df, production_df))

    outputs = list(electricity_residuals(context=None, datahub=_FakeDataHub()))

    assert len(outputs) == 2
    names = {o.output_name for o in outputs}
    assert names == {"electricity_consumption_pi", "electricity_production_report"}
    for output in outputs:
        assert isinstance(output.value, WarehouseTable)
        assert "row_count" in output.metadata


def test_steam_residuals_outputs(monkeypatch):
    # iloc[:-5] removes last 5 rows — need 7+ rows to get 2+ result rows
    consumption_df = pd.DataFrame(
        {
            "Receiver Cost Center": ["A", "B", "C", "D", "E", "F", "Total"],
            "Bldg #": ["1", "2", "3", "4", "5", "6", None],
            "Steam consumption Adjusted": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 210.0],
        }
    )
    production_df = pd.DataFrame({"item": ["Line 1"], "amount": [500.0]})

    monkeypatch.setattr(pd, "ExcelFile", lambda url, engine: "fake_wb")
    monkeypatch.setattr(pd, "read_excel", _sequential_read_excel(consumption_df, production_df))

    outputs = list(steam_residuals(context=None, datahub=_FakeDataHub()))

    assert len(outputs) == 2
    names = {o.output_name for o in outputs}
    assert names == {"steam_consumption_pi", "steam_production_report"}
    for output in outputs:
        assert isinstance(output.value, WarehouseTable)
        assert "row_count" in output.metadata


def test_chilled_water_residuals_outputs(monkeypatch):
    consumption_df = pd.DataFrame(
        {
            "Receiver Cost Center": ["X", "Y", "Total"],
            "Bldg #": ["10", "20", None],
            "Adjusted Usage": [5.0, 6.0, 11.0],
        }
    )
    production_df = pd.DataFrame({"item": ["Line 1"], "amount": [800.0]})

    monkeypatch.setattr(pd, "ExcelFile", lambda url, engine: "fake_wb")
    monkeypatch.setattr(pd, "read_excel", _sequential_read_excel(consumption_df, production_df))

    outputs = list(chilled_water_residuals(context=None, datahub=_FakeDataHub()))

    assert len(outputs) == 2
    names = {o.output_name for o in outputs}
    assert names == {"chilled_water_consumption_pi", "chilled_water_production_report"}
    for output in outputs:
        assert isinstance(output.value, WarehouseTable)
        assert "row_count" in output.metadata


def test_mthw_consumption_pi_output(monkeypatch):
    mthw_df = pd.DataFrame(
        {
            "Bldg #": ["E25", "E38", "Total"],
            "Receiver Cost Center": ["CC1", "CC2", "CC3"],
            "Metered Usage - MMBTU": [10.0, 20.0, 30.0],
            "Final Bill - kbtu": [9000.0, 18000.0, 27000.0],
        }
    )

    monkeypatch.setattr(pd, "ExcelFile", lambda url, engine: "fake_wb")
    monkeypatch.setattr(pd, "read_excel", _sequential_read_excel(mthw_df))

    result = mthw_consumption_pi(context=None, datahub=_FakeDataHub())

    assert isinstance(result, Output)
    assert isinstance(result.value, WarehouseTable)
    assert result.metadata["row_count"].value == 2
    assert result.value.columns == (
        "bldg_number",
        "receiver_cost_center",
        "metered_usage_-_mmbtu",
        "final_bill_-_kbtu",
    )


def test_assumed_rate_output(monkeypatch):
    class _FakeResponse:
        text = "utility,rate\nelectricity,0.12\nsteam,0.05"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "cockpit.css.assets.utility_rates.requests.get",
        lambda url, timeout: _FakeResponse(),
    )

    result = assumed_rate(context=None, datahub=_FakeDataHub())

    assert isinstance(result, Output)
    assert isinstance(result.value, WarehouseTable)
    assert result.metadata["row_count"].value == 2


def test_electricity_missing_project_raises():
    with pytest.raises(RuntimeError, match="not found"):
        list(electricity_residuals(context=None, datahub=_FakeDataHubNoProject()))


def test_electricity_missing_files_raises():
    with pytest.raises(RuntimeError, match="No files"):
        list(electricity_residuals(context=None, datahub=_FakeDataHubNoFiles()))


def test_steam_missing_project_raises():
    with pytest.raises(RuntimeError, match="not found"):
        list(steam_residuals(context=None, datahub=_FakeDataHubNoProject()))


def test_chilled_water_missing_project_raises():
    with pytest.raises(RuntimeError, match="not found"):
        list(chilled_water_residuals(context=None, datahub=_FakeDataHubNoProject()))


def test_assumed_rate_missing_project_raises():
    with pytest.raises(RuntimeError, match="not found"):
        assumed_rate(context=None, datahub=_FakeDataHubNoProject())


def test_mthw_missing_project_raises():
    with pytest.raises(RuntimeError, match="not found"):
        mthw_consumption_pi(context=None, datahub=_FakeDataHubNoProject())
