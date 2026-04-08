import os
from contextlib import contextmanager
from typing import Any, Iterator

from dagster import ConfigurableResource


class PostgresResource(ConfigurableResource):
    def connection_config(self, schema: str | None = None) -> dict[str, Any]:
        return {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "dbname": os.getenv("POSTGRES_DB", "delta_dev"),
            "schema": schema or os.getenv("DBT_SCHEMA_RAW", "src_byod_mitos"),
        }

    @contextmanager
    def connect(self, schema: str | None = None) -> Iterator[Any]:
        import psycopg2

        config = self.connection_config(schema=schema)
        active_schema = config.pop("schema", None)
        connection = psycopg2.connect(**config)
        if active_schema:
            cursor = connection.cursor()
            try:
                cursor.execute(f"SET search_path TO {active_schema}")
            finally:
                cursor.close()

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
