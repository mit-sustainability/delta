from dagster import AssetExecutionContext, MaterializeResult, asset

from ..resources import WarehouseResource
from ._shared import WAREHOUSE_PREFIX, WAREHOUSE_TARGET, escape_identifier

WAREHOUSE_SMOKE_SOURCE_NAME = "warehouse_smoke"
WAREHOUSE_SMOKE_TABLE = "warehouse_test_input"
WAREHOUSE_SMOKE_ROWS = [
    ("1", "Delta Platform", "12.50", "2026-01-01T00:00:00"),
    ("2", "Snowflake Path", "7.25", "2026-01-02T06:30:00"),
    ("3", "Postgres Path", "3.00", "2026-01-03T12:45:00"),
]


def _snowflake_relation(schema: str, table: str) -> str:
    return f"{schema.lower()}.{table.lower()}"


@asset(
    key_prefix=[WAREHOUSE_PREFIX, WAREHOUSE_SMOKE_SOURCE_NAME],
    group_name="raw",
    required_resource_keys={"warehouse"},
)
def warehouse_test_input(context: AssetExecutionContext) -> MaterializeResult:
    warehouse: WarehouseResource = context.resources.warehouse
    config = warehouse.connection_config()
    kind = config["kind"]
    schema = config["schema"]
    snowflake_relation = _snowflake_relation(schema, WAREHOUSE_SMOKE_TABLE)
    postgres_relation = f'"{escape_identifier(schema)}"."{WAREHOUSE_SMOKE_TABLE}"'
    relation = postgres_relation if kind == "postgres" else snowflake_relation

    with warehouse.connect() as connection:
        cursor = connection.cursor()
        try:
            if kind == "postgres":
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{escape_identifier(schema)}"')
                cursor.execute(f"DROP TABLE IF EXISTS {relation}")
                cursor.execute(
                    f'''
                    CREATE TABLE {relation} (
                        id TEXT NOT NULL,
                        platform_name TEXT NOT NULL,
                        amount TEXT NOT NULL,
                        loaded_at TEXT NOT NULL
                    )
                    '''
                )
            else:
                cursor.execute(
                    f'''
                    CREATE OR REPLACE TABLE {snowflake_relation} (
                        id VARCHAR NOT NULL,
                        platform_name VARCHAR NOT NULL,
                        amount VARCHAR NOT NULL,
                        loaded_at VARCHAR NOT NULL
                    )
                    '''
                )

            cursor.executemany(
                f'''
                INSERT INTO {relation} (
                    id, platform_name, amount, loaded_at
                ) VALUES (%s, %s, %s, %s)
                ''',
                WAREHOUSE_SMOKE_ROWS,
            )
            connection.commit()
        finally:
            cursor.close()

    return MaterializeResult(
        metadata={
            "warehouse_target": WAREHOUSE_TARGET,
            "warehouse_kind": kind,
            "raw_schema": schema,
            "raw_table": WAREHOUSE_SMOKE_TABLE,
            "row_count": len(WAREHOUSE_SMOKE_ROWS),
        }
    )
