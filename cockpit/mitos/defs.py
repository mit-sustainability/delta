import os

from dagster import Definitions

from .assets import mitos_assets, mitos_postgres_dbt_assets, mitos_snowflake_dbt_assets
from .jobs import mitos_job

warehouse_target = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))

active_dbt_assets = (
    mitos_postgres_dbt_assets if warehouse_target == "local" else mitos_snowflake_dbt_assets
)

mitos_defs = Definitions(
    assets=[*mitos_assets, active_dbt_assets],
    jobs=[mitos_job],
)
