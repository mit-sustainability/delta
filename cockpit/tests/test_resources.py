import sys
from types import SimpleNamespace

from cockpit.resources import WarehouseResource


def test_local_connection_config(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "delta_dev")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")

    resource = WarehouseResource(target="local")

    assert resource.connection_config() == {
        "kind": "postgres",
        "host": "localhost",
        "user": "postgres",
        "password": "postgres",
        "port": 5432,
        "dbname": "delta_dev",
        "schema": "src_byod_mitos",
    }


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

    resource = WarehouseResource(target="prod")

    assert resource.connection_config() == {
        "kind": "snowflake",
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

    resource = WarehouseResource(target="prod")

    assert resource.connection_config() == {
        "kind": "snowflake",
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

    resource = WarehouseResource(target="prod")

    assert resource.connection_config() == {
        "kind": "snowflake",
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
        "cockpit.resources.warehouse._load_snowflake_private_key",
        lambda path, passphrase: b"private-key-bytes",
    )

    resource = WarehouseResource(target="prod")

    assert resource.resolved_connection_config() == {
        "kind": "snowflake",
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

    class _FakeConnection:
        def close(self):
            return None

    def _fake_connect(**kwargs):
        captured.update(kwargs)
        return _FakeConnection()

    monkeypatch.setitem(sys.modules, "psycopg2", SimpleNamespace(connect=_fake_connect))

    resource = WarehouseResource(target="local")

    with resource.connect():
        pass

    assert captured == {
        "host": "localhost",
        "user": "postgres",
        "password": "postgres",
        "port": 5432,
        "dbname": "delta_dev",
    }
