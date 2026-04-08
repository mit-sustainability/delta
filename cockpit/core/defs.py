import os

from dagster import Definitions

from ..scopes import CORE_SCOPE
from ..shared.resources import build_warehouse_io_manager
from .assets import core_assets
from .jobs import core_jobs

warehouse_target = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))

core_defs = Definitions(
    assets=core_assets,
    jobs=core_jobs,
    resources={
        "raw_io_manager": build_warehouse_io_manager(
            target=warehouse_target,
            schema=CORE_SCOPE.raw_schema(),
        )
    },
)
