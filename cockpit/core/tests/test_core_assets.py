from dagster import AssetKey, Definitions

from cockpit.core.assets import warehouse_test_input
from cockpit.core.defs import core_defs
from cockpit.scopes import CORE_SCOPE
from cockpit.shared.resources import (
    PostgresResource,
    PostgresWarehouseIOManager,
    SnowflakeResource,
    SnowflakeWarehouseIOManager,
    WarehouseTable,
)


def test_core_defs_is_definitions():
    assert isinstance(core_defs, Definitions)


class _FakeCursor:
    def __init__(self):
        self.statements = []
        self.executemany_calls = []

    def execute(self, sql, parameters=None):
        self.statements.append((sql, parameters))

    def executemany(self, sql, parameters):
        self.executemany_calls.append((sql, list(parameters)))

    def close(self):
        return None


class _FakeConnection:
    def __init__(self):
        self.cursor_instance = _FakeCursor()
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


class _FakeOutputContext:
    def __init__(self):
        self.asset_key = AssetKey(["core", "warehouse_smoke", "warehouse_test_input"])
        self.metadata = {}

    def add_output_metadata(self, metadata):
        self.metadata.update(metadata)


class _connection_context:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        return False


def test_warehouse_test_input_returns_table_payload():
    result = warehouse_test_input()

    assert isinstance(result.value, WarehouseTable)
    assert result.value.name == "warehouse_test_input"
    assert result.metadata["scope"].value == "core"
    assert result.metadata["raw_table"].value == "warehouse_test_input"
    assert result.metadata["row_count"].value == 3


def test_warehouse_table_io_manager_writes_postgres_sql(monkeypatch):
    fake_connection = _FakeConnection()
    monkeypatch.setattr(
        PostgresResource,
        "connect",
        lambda self, schema=None: _connection_context(fake_connection),
    )
    io_manager = PostgresWarehouseIOManager(target_schema=CORE_SCOPE.raw_schema())
    context = _FakeOutputContext()

    io_manager.handle_output(context, warehouse_test_input().value)

    statements = [sql for sql, _ in fake_connection.cursor_instance.statements]
    assert any("CREATE SCHEMA IF NOT EXISTS" in sql for sql in statements)
    assert any("DROP TABLE IF EXISTS" in sql for sql in statements)
    assert fake_connection.cursor_instance.executemany_calls
    assert fake_connection.commits == 1
    assert context.metadata["warehouse_kind"] == "postgres"
    assert context.metadata["raw_schema"] == CORE_SCOPE.raw_schema()


def test_warehouse_table_io_manager_writes_snowflake_sql(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "secret")
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")

    fake_connection = _FakeConnection()
    monkeypatch.setattr(
        SnowflakeResource,
        "connect",
        lambda self, schema=None: _connection_context(fake_connection),
    )
    io_manager = SnowflakeWarehouseIOManager(target_schema=CORE_SCOPE.raw_schema())
    context = _FakeOutputContext()

    io_manager.handle_output(context, warehouse_test_input().value)

    statements = [sql for sql, _ in fake_connection.cursor_instance.statements]
    assert any("CREATE OR REPLACE TABLE" in sql for sql in statements)
    assert any("src_byod_core.warehouse_test_input" in sql for sql in statements)
    assert not any("CREATE SCHEMA IF NOT EXISTS" in sql for sql in statements)
    assert fake_connection.cursor_instance.executemany_calls
    insert_sql, _ = fake_connection.cursor_instance.executemany_calls[0]
    assert "src_byod_core.warehouse_test_input" in insert_sql
    assert fake_connection.commits == 1
    assert context.metadata["warehouse_kind"] == "snowflake"
