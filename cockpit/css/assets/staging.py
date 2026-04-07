from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

from ...dbt_project import delta_dbt_project
from ...scopes import CSS_SCOPE
from ...shared.resources import PrefixTranslator


@dbt_assets(
    manifest=delta_dbt_project.manifest_path,
    select=f"path:{CSS_SCOPE.dbt_path}",
    dagster_dbt_translator=PrefixTranslator("postgres"),
)
def css_postgres_dbt_assets(context: AssetExecutionContext, dbt_postgres: DbtCliResource):
    yield from dbt_postgres.cli(["build", "--target", "local"], context=context).stream()


@dbt_assets(
    manifest=delta_dbt_project.manifest_path,
    select=f"path:{CSS_SCOPE.dbt_path}",
    dagster_dbt_translator=PrefixTranslator("snowflake"),
)
def css_snowflake_dbt_assets(context: AssetExecutionContext, dbt_snowflake: DbtCliResource):
    yield from dbt_snowflake.cli(["build", "--target", "prod"], context=context).stream()
