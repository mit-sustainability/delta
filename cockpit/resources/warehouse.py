import os
from contextlib import contextmanager
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
                "password": os.getenv("SNOWFLAKE_PASSWORD"),
                "role": os.getenv("SNOWFLAKE_ROLE"),
                "database": os.getenv("SNOWFLAKE_DATABASE"),
                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                "schema": os.getenv("DBT_SCHEMA_RAW", "src_byod_mitos"),
                "authenticator": os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
            }
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

    @contextmanager
    def connect(self) -> Iterator[Any]:
        config = self.connection_config()
        kind = config.pop("kind")

        if kind == "snowflake":
            import snowflake.connector

            connection = snowflake.connector.connect(**config)
        else:
            import psycopg2

            schema = config.pop("schema", None)
            connection = psycopg2.connect(**config)
            if schema:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"SET search_path TO {schema}")
                finally:
                    cursor.close()

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
