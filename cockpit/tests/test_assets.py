from dagster import build_asset_context

from cockpit.assets import warehouse_test_input
from cockpit.resources import WarehouseResource


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


def test_warehouse_test_input_writes_postgres_sql(monkeypatch):
    fake_connection = _FakeConnection()
    monkeypatch.setattr(
        WarehouseResource,
        "connect",
        lambda self: _connection_context(fake_connection),
    )

    context = build_asset_context(resources={"warehouse": WarehouseResource(target="local")})
    result = warehouse_test_input(context)

    statements = [sql for sql, _ in fake_connection.cursor_instance.statements]
    assert any("CREATE SCHEMA IF NOT EXISTS" in sql for sql in statements)
    assert any("DROP TABLE IF EXISTS" in sql for sql in statements)
    assert fake_connection.cursor_instance.executemany_calls
    assert fake_connection.commits == 1
    assert result.metadata["warehouse_kind"] == "postgres"


def test_warehouse_test_input_writes_snowflake_sql(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "secret")
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")

    fake_connection = _FakeConnection()
    monkeypatch.setattr(
        WarehouseResource,
        "connect",
        lambda self: _connection_context(fake_connection),
    )

    context = build_asset_context(resources={"warehouse": WarehouseResource(target="prod")})
    result = warehouse_test_input(context)

    statements = [sql for sql, _ in fake_connection.cursor_instance.statements]
    assert any("CREATE OR REPLACE TABLE" in sql for sql in statements)
    assert any("src_byod_mitos.warehouse_test_input" in sql for sql in statements)
    assert not any("CREATE SCHEMA IF NOT EXISTS" in sql for sql in statements)
    assert fake_connection.cursor_instance.executemany_calls
    insert_sql, _ = fake_connection.cursor_instance.executemany_calls[0]
    assert "src_byod_mitos.warehouse_test_input" in insert_sql
    assert fake_connection.commits == 1
    assert result.metadata["warehouse_kind"] == "snowflake"


class _connection_context:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        return False
