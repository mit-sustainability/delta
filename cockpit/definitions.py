import os

from dagster import Definitions
from dagster_dbt import DbtCliResource

from .assets import postgres_dbt_assets, snowflake_dbt_assets
from .project import delta_dbt_project
from .resources import WarehouseResource

warehouse_target = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))

defs = Definitions(
    assets=[postgres_dbt_assets, snowflake_dbt_assets],
    resources={
        # Two dbt resources, each can use different target settings
        "dbt_postgres": DbtCliResource(project_dir=delta_dbt_project),
        "dbt_snowflake": DbtCliResource(project_dir=delta_dbt_project),
        "warehouse": WarehouseResource(target=warehouse_target),
    },
)
