from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

from ..dbt_project import delta_dbt_project
from ._shared import PrefixTranslator


# PostgreSQL-backed dbt assets for local development and test workflows.
@dbt_assets(
    manifest=delta_dbt_project.manifest_path,
    select="*",
    dagster_dbt_translator=PrefixTranslator("postgres"),
)
def postgres_dbt_assets(context: AssetExecutionContext, dbt_postgres: DbtCliResource):
    yield from dbt_postgres.cli(["build", "--target", "local"], context=context).stream()


# Snowflake-backed dbt assets for target-state production runs.
@dbt_assets(
    manifest=delta_dbt_project.manifest_path,
    select="*",
    dagster_dbt_translator=PrefixTranslator("snowflake"),
)
def snowflake_dbt_assets(context: AssetExecutionContext, dbt_snowflake: DbtCliResource):
    yield from dbt_snowflake.cli(["build", "--target", "prod"], context=context).stream()
