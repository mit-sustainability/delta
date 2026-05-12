import os

from dagster import Definitions

from ..scopes import CSS_SCOPE
from ..shared.resources import build_warehouse_io_manager
from ..shared.resources.datahub import DataHubResource
from .assets import css_assets, css_postgres_dbt_assets, css_snowflake_dbt_assets
from .jobs import css_job

warehouse_target = os.getenv("DBT_TARGET", "local")

active_dbt_assets = (
    css_postgres_dbt_assets if warehouse_target == "local" else css_snowflake_dbt_assets
)

css_defs = Definitions(
    assets=[*css_assets, active_dbt_assets],
    jobs=[css_job],
    resources={
        "css_raw_io_manager": build_warehouse_io_manager(
            target=warehouse_target,
            schema=CSS_SCOPE.raw_schema(),
        ),
        "datahub": DataHubResource(
            auth_token=os.getenv("DATAHUB_API_KEY", ""),
        ),
    },
)
