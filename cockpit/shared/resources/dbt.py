import os
from typing import Any, Mapping

from dagster import AssetKey
from dagster_dbt import DagsterDbtTranslator, DbtCliResource

from ...dbt_project import delta_dbt_project

WAREHOUSE_TARGET = os.getenv("DBT_TARGET", "local")
WAREHOUSE_PREFIX = "snowflake" if WAREHOUSE_TARGET == "prod" else "postgres"


class PrefixTranslator(DagsterDbtTranslator):
    def __init__(self, prefix: str, source_prefix: list[str] | None = None):
        super().__init__()
        self._prefix = prefix
        self._source_prefix = source_prefix

    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
        if dbt_resource_props.get("resource_type") == "source":
            if self._source_prefix is not None:
                return AssetKey([*self._source_prefix, dbt_resource_props["name"]])
            return super().get_asset_key(dbt_resource_props)
        return super().get_asset_key(dbt_resource_props).with_prefix(self._prefix)

    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> str:
        # fqn: ['project', 'scope', 'layer', 'model'] — scope is index 1
        fqn = dbt_resource_props.get("fqn", [])
        return fqn[1] if len(fqn) > 1 else "default"


def build_dbt_resource() -> DbtCliResource:
    return DbtCliResource(project_dir=delta_dbt_project)
