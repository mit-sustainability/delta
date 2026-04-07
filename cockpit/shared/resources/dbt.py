import os
from typing import Any, Mapping

from dagster import AssetKey
from dagster_dbt import DagsterDbtTranslator, DbtCliResource

from ...dbt_project import delta_dbt_project

WAREHOUSE_TARGET = os.getenv("WAREHOUSE_TARGET", os.getenv("DBT_TARGET", "local"))
WAREHOUSE_PREFIX = "snowflake" if WAREHOUSE_TARGET == "prod" else "postgres"


class PrefixTranslator(DagsterDbtTranslator):
    def __init__(self, prefix: str):
        self._prefix = prefix

    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
        return super().get_asset_key(dbt_resource_props).with_prefix(self._prefix)


def build_dbt_resource() -> DbtCliResource:
    return DbtCliResource(project_dir=delta_dbt_project)
