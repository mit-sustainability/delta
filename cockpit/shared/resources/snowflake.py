import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from dagster import ConfigurableResource


class SnowflakeResource(ConfigurableResource):
    def connection_config(self, schema: str | None = None) -> dict[str, Any]:
        config = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "role": os.getenv("SNOWFLAKE_ROLE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "schema": schema or os.getenv("DBT_SCHEMA_RAW", "src_byod_mitos"),
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
                config["authenticator"] = os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser")
        return {key: value for key, value in config.items() if value not in (None, "")}

    def resolved_connection_config(self, schema: str | None = None) -> dict[str, Any]:
        config = dict(self.connection_config(schema=schema))

        if "private_key_path" in config:
            private_key_path = config.pop("private_key_path")
            private_key_passphrase = config.pop("private_key_passphrase", None)
            config["private_key"] = _load_snowflake_private_key(
                private_key_path, private_key_passphrase
            )

        return config

    @contextmanager
    def connect(self, schema: str | None = None) -> Iterator[Any]:
        import snowflake.connector

        config = self.resolved_connection_config(schema=schema)
        connection = snowflake.connector.connect(**config)

        try:
            yield connection
        finally:
            connection.close()

    def execute(
        self,
        sql: str,
        parameters: tuple[Any, ...] | None = None,
        schema: str | None = None,
    ) -> None:
        with self.connect(schema=schema) as connection:
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
