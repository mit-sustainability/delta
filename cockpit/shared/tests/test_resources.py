import importlib
import sys
from types import SimpleNamespace

import cockpit.definitions as definitions_module
from cockpit import defs
from cockpit.css.defs import css_defs
from cockpit.mitos.defs import mitos_defs
from cockpit.scopes import CSS_SCOPE, MITOS_SCOPE
from cockpit.shared.resources import (
    PostgresResource,
    PostgresWarehouseIOManager,
    SnowflakeResource,
    SnowflakeWarehouseIOManager,
    build_warehouse_io_manager,
)


def test_dagster_definitions():
    assert defs.resolve_job_def("mitos_job").name == "mitos_job"
    assert defs.resolve_job_def("css_job").name == "css_job"


def test_definitions_select_local_dbt_resource(monkeypatch):
    monkeypatch.setenv("DBT_TARGET", "local")
    monkeypatch.delenv("WAREHOUSE_TARGET", raising=False)

    reloaded = importlib.reload(definitions_module)
    job_names = {job.name for job in reloaded.defs.jobs}

    assert reloaded.warehouse_target == "local"
    assert "dbt_postgres" in reloaded.resources
    assert "dbt_snowflake" not in reloaded.resources
    assert "raw_io_manager" in reloaded.defs.resources
    assert "mitos_job" in job_names
    assert "css_job" in job_names


def test_definitions_select_prod_dbt_resource(monkeypatch):
    monkeypatch.setenv("DBT_TARGET", "local")
    monkeypatch.setenv("WAREHOUSE_TARGET", "prod")

    reloaded = importlib.reload(definitions_module)
    job_names = {job.name for job in reloaded.defs.jobs}

    assert reloaded.warehouse_target == "prod"
    assert "dbt_snowflake" in reloaded.resources
    assert "dbt_postgres" not in reloaded.resources
    assert "raw_io_manager" in reloaded.defs.resources
    assert "mitos_job" in job_names
    assert "css_job" in job_names


def test_local_connection_config(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "delta_dev")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")

    resource = PostgresResource()

    assert resource.connection_config() == {
        "host": "localhost",
        "user": "postgres",
        "password": "postgres",
        "port": 5432,
        "dbname": "delta_dev",
        "schema": "src_byod_mitos",
    }


def test_connection_config_accepts_schema_override(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "delta_dev")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")

    resource = PostgresResource()

    assert resource.connection_config(schema="src_byod_css")["schema"] == "src_byod_css"


def test_prod_connection_config_prefers_private_key(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "secret")
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")
    monkeypatch.setenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser")
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_PATH", "/tmp/snowflake.p8")
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "passphrase")

    resource = SnowflakeResource()

    assert resource.connection_config() == {
        "account": "account",
        "user": "user",
        "role": "role",
        "database": "database",
        "warehouse": "warehouse",
        "schema": "src_byod_mitos",
        "private_key_path": "/tmp/snowflake.p8",
        "private_key_passphrase": "passphrase",
    }


def test_prod_connection_config_falls_back_to_password(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "secret")
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_PATH", raising=False)
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", raising=False)
    monkeypatch.delenv("SNOWFLAKE_AUTHENTICATOR", raising=False)

    resource = SnowflakeResource()

    assert resource.connection_config() == {
        "account": "account",
        "user": "user",
        "password": "secret",
        "role": "role",
        "database": "database",
        "warehouse": "warehouse",
        "schema": "src_byod_mitos",
    }


def test_prod_connection_config_falls_back_to_externalbrowser(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.delenv("SNOWFLAKE_PASSWORD", raising=False)
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_PATH", raising=False)
    monkeypatch.setenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser")

    resource = SnowflakeResource()

    assert resource.connection_config() == {
        "account": "account",
        "user": "user",
        "role": "role",
        "database": "database",
        "warehouse": "warehouse",
        "schema": "src_byod_mitos",
        "authenticator": "externalbrowser",
    }


def test_resolved_connection_config_loads_private_key(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_PATH", "/tmp/snowflake.p8")
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "passphrase")
    monkeypatch.setattr(
        "cockpit.shared.resources.snowflake._load_snowflake_private_key",
        lambda path, passphrase: b"private-key-bytes",
    )

    resource = SnowflakeResource()

    assert resource.resolved_connection_config() == {
        "account": "account",
        "user": "user",
        "role": "role",
        "database": "database",
        "warehouse": "warehouse",
        "schema": "src_byod_mitos",
        "private_key": b"private-key-bytes",
    }


def test_postgres_connect_omits_schema_kwarg(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "delta_dev")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")

    captured = {}

    class _FakeCursor:
        def execute(self, sql):
            captured["set_search_path_sql"] = sql

        def close(self):
            return None

    class _FakeConnection:
        def cursor(self):
            return _FakeCursor()

        def close(self):
            return None

    def _fake_connect(**kwargs):
        captured.update(kwargs)
        return _FakeConnection()

    monkeypatch.setitem(sys.modules, "psycopg2", SimpleNamespace(connect=_fake_connect))

    resource = PostgresResource()

    with resource.connect():
        pass

    assert captured == {
        "host": "localhost",
        "user": "postgres",
        "password": "postgres",
        "port": 5432,
        "dbname": "delta_dev",
        "set_search_path_sql": "SET search_path TO src_byod_mitos",
    }


def test_build_warehouse_io_manager_selects_by_target():
    assert isinstance(build_warehouse_io_manager("local", "src"), PostgresWarehouseIOManager)
    assert isinstance(build_warehouse_io_manager("prod", "src"), SnowflakeWarehouseIOManager)


def test_scope_defs_bind_raw_io_manager_from_scope_metadata():
    assert MITOS_SCOPE.raw_schema() == "src_byod_mitos"
    assert CSS_SCOPE.raw_schema() == "src_byod_css"
    assert mitos_defs.resources is None
    assert css_defs.resources is None


def test_postgres_warehouse_io_manager_rejects_load_input():
    io_manager = PostgresWarehouseIOManager(target_schema="src_byod_mitos")

    try:
        io_manager.load_input(None)
    except NotImplementedError as exc:
        assert "does not support loading inputs" in str(exc)
    else:
        raise AssertionError("Expected load_input to raise NotImplementedError")


def test_snowflake_warehouse_io_manager_rejects_load_input():
    io_manager = SnowflakeWarehouseIOManager(target_schema="src_byod_mitos")

    try:
        io_manager.load_input(None)
    except NotImplementedError as exc:
        assert "does not support loading inputs" in str(exc)
    else:
        raise AssertionError("Expected load_input to raise NotImplementedError")
