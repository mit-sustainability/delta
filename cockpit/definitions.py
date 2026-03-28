import os

from dagster import Definitions
from dagster_dbt import DbtCliResource

from .assets import postgres_dbt_assets, snowflake_dbt_assets, warehouse_test_input
from .dbt_project import delta_dbt_project
from .resources import WarehouseResource

warehouse_target = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))

active_dbt_assets = postgres_dbt_assets if warehouse_target == "local" else snowflake_dbt_assets
active_dbt_resource_key = "dbt_postgres" if warehouse_target == "local" else "dbt_snowflake"

resources = {
    "warehouse": WarehouseResource(target=warehouse_target),
    active_dbt_resource_key: DbtCliResource(project_dir=delta_dbt_project),
}

defs = Definitions(
    assets=[warehouse_test_input, active_dbt_assets],
    resources=resources,
)
