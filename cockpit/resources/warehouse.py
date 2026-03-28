import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Literal

from dagster import ConfigurableResource

WarehouseTarget = Literal["local", "prod"]


class WarehouseResource(ConfigurableResource):
    """Warehouse connection helper that switches between local Postgres and prod Snowflake."""

    target: WarehouseTarget = "local"

    def connection_config(self) -> dict[str, Any]:
        if self.target == "prod":
            config = {
                "kind": "snowflake",
                "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                "user": os.getenv("SNOWFLAKE_USER"),
                "role": os.getenv("SNOWFLAKE_ROLE"),
                "database": os.getenv("SNOWFLAKE_DATABASE"),
                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                "schema": os.getenv("DBT_SCHEMA_RAW", "src_byod_mitos"),
            }
            private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
            if private_key_path:
                config["private_key_path"] = private_key_path
                private_key_passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
                if private_key_passphrase:
                    config["private_key_passphrase"] = private_key_passphrase
            else:
                password = os.getenv("SNOWFLAKE_PASSWORD")
                if password:
                    config["password"] = password
                else:
                    config["authenticator"] = os.getenv(
                        "SNOWFLAKE_AUTHENTICATOR", "externalbrowser"
                    )
            return {key: value for key, value in config.items() if value not in (None, "")}

        return {
            "kind": "postgres",
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "dbname": os.getenv("POSTGRES_DB", "delta_dev"),
            "schema": os.getenv("DBT_SCHEMA_RAW", "src_byod_mitos"),
        }

    def resolved_connection_config(self) -> dict[str, Any]:
        config = dict(self.connection_config())
        kind = config.get("kind")

        if kind == "snowflake" and "private_key_path" in config:
            private_key_path = config.pop("private_key_path")
            private_key_passphrase = config.pop("private_key_passphrase", None)
            config["private_key"] = _load_snowflake_private_key(
                private_key_path, private_key_passphrase
            )

        return config

    @contextmanager
    def connect(self) -> Iterator[Any]:
        config = self.resolved_connection_config()
        kind = config.pop("kind")

        if kind == "snowflake":
            import snowflake.connector

            connection = snowflake.connector.connect(**config)
        else:
            import psycopg2

            # Keep schema available to callers building SQL, but don't pass it to psycopg2.
            config.pop("schema", None)
            connection = psycopg2.connect(**config)

        try:
            yield connection
        finally:
            connection.close()

    def execute(self, sql: str, parameters: tuple[Any, ...] | None = None) -> None:
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(sql, parameters)
                connection.commit()
            finally:
                cursor.close()


def _load_snowflake_private_key(
    private_key_path: str, private_key_passphrase: str | None = None
) -> bytes:
    from cryptography.hazmat.primitives import serialization

    password = private_key_passphrase.encode() if private_key_passphrase else None
    private_key = serialization.load_pem_private_key(
        Path(private_key_path).expanduser().read_bytes(),
        password=password,
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
