from pathlib import Path

from dagster_dbt import DbtProject

dbt_project_dir = Path(__file__).joinpath("..", "..", "dbt").resolve()

# We use the same manifest for both targets as the model structure is identical.
# The target only changes where the queries are executed.
delta_dbt_project = DbtProject(
    project_dir=dbt_project_dir,
)
delta_dbt_project.prepare_if_dev()
