from dagster import Output, asset

from ...shared.resources import WarehouseTable

WAREHOUSE_SMOKE_SOURCE_NAME = "warehouse_smoke"
WAREHOUSE_SMOKE_TABLE = "warehouse_test_input"
WAREHOUSE_SMOKE_ROWS = [
    ("1", "Delta Platform", "12.50", "2026-01-01T00:00:00"),
    ("2", "Snowflake Path", "7.25", "2026-01-02T06:30:00"),
    ("3", "Postgres Path", "3.00", "2026-01-03T12:45:00"),
]


@asset(
    key_prefix=["core", WAREHOUSE_SMOKE_SOURCE_NAME],
    group_name="core",
    tags={"layer": "raw"},
    io_manager_key="raw_io_manager",
)
def warehouse_test_input() -> Output[WarehouseTable]:
    return Output(
        value=WarehouseTable(
            name=WAREHOUSE_SMOKE_TABLE,
            columns=("id", "platform_name", "amount", "loaded_at"),
            rows=tuple(WAREHOUSE_SMOKE_ROWS),
        ),
        metadata={
            "scope": "core",
            "raw_table": WAREHOUSE_SMOKE_TABLE,
            "row_count": len(WAREHOUSE_SMOKE_ROWS),
        },
    )
