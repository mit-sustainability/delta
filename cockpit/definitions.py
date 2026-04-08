import os

from dagster import Definitions

from .core import defs as core_defs_module
from .css import defs as css_defs_module
from .mitos import defs as mitos_defs_module
from .shared.resources import build_dbt_resource
from .shared.schedules import global_schedules
from .shared.sensors import global_sensors

warehouse_target = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))
active_dbt_resource_key = "dbt_postgres" if warehouse_target == "local" else "dbt_snowflake"

resources = {
    active_dbt_resource_key: build_dbt_resource(),
}

defs = Definitions.merge(
    core_defs_module.core_defs,
    mitos_defs_module.mitos_defs,
    css_defs_module.css_defs,
    Definitions(
        resources=resources,
        schedules=global_schedules,
        sensors=global_sensors,
    ),
)
