from dataclasses import dataclass
from typing import Any

from dagster import ConfigurableIOManager

from .postgres import PostgresResource
from .snowflake import SnowflakeResource


@dataclass(frozen=True)
class WarehouseTable:
    name: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


class PostgresWarehouseIOManager(ConfigurableIOManager):
    target_schema: str

    def handle_output(self, context, obj: WarehouseTable) -> None:
        warehouse = PostgresResource()
        relation = self._relation(obj.name)

        with warehouse.connect(schema=self.target_schema) as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{self._escape(self.target_schema)}"')
                cursor.execute(f"DROP TABLE IF EXISTS {relation}")
                column_sql = ", ".join(
                    f"{self._column_identifier(column)} TEXT NOT NULL" for column in obj.columns
                )
                cursor.execute(f"CREATE TABLE {relation} ({column_sql})")

                placeholders = ", ".join(["%s"] * len(obj.columns))
                column_names = ", ".join(self._column_identifier(column) for column in obj.columns)
                cursor.executemany(
                    f"INSERT INTO {relation} ({column_names}) VALUES ({placeholders})",
                    obj.rows,
                )
                connection.commit()
            finally:
                cursor.close()

        context.add_output_metadata(
            {
                "raw_schema": self.target_schema,
                "raw_table": obj.name,
                "row_count": len(obj.rows),
                "warehouse_kind": "postgres",
            }
        )

    def load_input(self, context) -> Any:
        raise NotImplementedError("PostgresWarehouseIOManager does not support loading inputs.")

    def _relation(self, table: str) -> str:
        return f'"{self._escape(self.target_schema)}"."{table}"'

    def _column_identifier(self, name: str) -> str:
        return f'"{self._escape(name)}"'

    def _escape(self, identifier: str) -> str:
        return identifier.replace('"', '""')


class SnowflakeWarehouseIOManager(ConfigurableIOManager):
    target_schema: str

    def handle_output(self, context, obj: WarehouseTable) -> None:
        warehouse = SnowflakeResource()
        relation = f"{self.target_schema.lower()}.{obj.name.lower()}"

        with warehouse.connect(schema=self.target_schema) as connection:
            cursor = connection.cursor()
            try:
                column_sql = ", ".join(
                    f"{self._column_identifier(column)} VARCHAR NOT NULL" for column in obj.columns
                )
                cursor.execute(f"CREATE OR REPLACE TABLE {relation} ({column_sql})")

                placeholders = ", ".join(["%s"] * len(obj.columns))
                column_names = ", ".join(self._column_identifier(column) for column in obj.columns)
                cursor.executemany(
                    f"INSERT INTO {relation} ({column_names}) VALUES ({placeholders})",
                    obj.rows,
                )
                connection.commit()
            finally:
                cursor.close()

        context.add_output_metadata(
            {
                "raw_schema": self.target_schema,
                "raw_table": obj.name,
                "row_count": len(obj.rows),
                "warehouse_kind": "snowflake",
            }
        )

    def load_input(self, context) -> Any:
        raise NotImplementedError("SnowflakeWarehouseIOManager does not support loading inputs.")

    def _column_identifier(self, name: str) -> str:
        return f'"{name.replace(chr(34), chr(34) * 2)}"'


def build_warehouse_io_manager(target: str, schema: str):
    if target == "prod":
        return SnowflakeWarehouseIOManager(target_schema=schema)
    return PostgresWarehouseIOManager(target_schema=schema)
