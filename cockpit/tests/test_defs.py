import importlib

from dagster import Definitions

import cockpit.definitions as definitions_module
from cockpit import defs


def test_dagster_definitions():
    assert isinstance(defs, Definitions)


def test_definitions_select_local_dbt_resource(monkeypatch):
    monkeypatch.setenv("DBT_TARGET", "local")
    monkeypatch.delenv("WAREHOUSE_TARGET", raising=False)

    reloaded = importlib.reload(definitions_module)

    assert reloaded.warehouse_target == "local"
    assert "dbt_postgres" in reloaded.resources
    assert "dbt_snowflake" not in reloaded.resources


def test_definitions_select_prod_dbt_resource(monkeypatch):
    monkeypatch.setenv("DBT_TARGET", "local")
    monkeypatch.setenv("WAREHOUSE_TARGET", "prod")

    reloaded = importlib.reload(definitions_module)

    assert reloaded.warehouse_target == "prod"
    assert "dbt_snowflake" in reloaded.resources
    assert "dbt_postgres" not in reloaded.resources
