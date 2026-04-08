import os

from dagster import Definitions

from .assets import css_assets, css_postgres_dbt_assets, css_snowflake_dbt_assets
from .jobs import css_job

warehouse_target = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))

active_dbt_assets = (
    css_postgres_dbt_assets if warehouse_target == "local" else css_snowflake_dbt_assets
)

css_defs = Definitions(
    assets=[*css_assets, active_dbt_assets],
    jobs=[css_job],
)
