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


def test_prod_connection_config_omits_empty_password(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "account")
    monkeypatch.setenv("SNOWFLAKE_USER", "user")
    monkeypatch.delenv("SNOWFLAKE_PASSWORD", raising=False)
    monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "database")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "warehouse")
    monkeypatch.setenv("DBT_SCHEMA_RAW", "src_byod_mitos")
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
