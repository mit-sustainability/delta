from typing import Any, Mapping

from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets

from .project import delta_dbt_project


class _PrefixTranslator(DagsterDbtTranslator):
    def __init__(self, prefix: str):
        self._prefix = prefix

    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
        return super().get_asset_key(dbt_resource_props).with_prefix(self._prefix)


# PostgreSQL-backed dbt assets for local development and test workflows.
@dbt_assets(
    manifest=delta_dbt_project.manifest_path,
    select="*",
    dagster_dbt_translator=_PrefixTranslator("postgres"),
)
def postgres_dbt_assets(context: AssetExecutionContext, dbt_postgres: DbtCliResource):
    yield from dbt_postgres.cli(["build", "--target", "local"], context=context).stream()

# Snowflake-backed dbt assets for target-state production runs.
@dbt_assets(
    manifest=delta_dbt_project.manifest_path,
    select="*",
    dagster_dbt_translator=_PrefixTranslator("snowflake"),
)
def snowflake_dbt_assets(context: AssetExecutionContext, dbt_snowflake: DbtCliResource):
    yield from dbt_snowflake.cli(["build", "--target", "prod"], context=context).stream()
