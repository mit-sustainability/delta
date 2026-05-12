import os
from io import StringIO

import pandas as pd
import requests
from dagster import AssetExecutionContext, AssetOut, Output, asset, multi_asset

from ...shared.resources import WarehouseTable
from ...shared.resources.datahub import DataHubResource

# Override via env to point at a specific DataHub project and file
DATAHUB_PROJECT_NAME = os.getenv("CSS_DATAHUB_PROJECT_NAME", "CSS Project")
DATAHUB_FILE_SEARCH_TERM = os.getenv("CSS_DATAHUB_FILE_TERM", "css_data")


@asset(
    key_prefix=["css", "datahub"],
    group_name="css",
    tags={"layer": "raw"},
    io_manager_key="css_raw_io_manager",
)
def css_datahub_source(
    context: AssetExecutionContext,
    datahub: DataHubResource,
) -> Output[WarehouseTable]:
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    urls = datahub.search_files_from_project(project_id, DATAHUB_FILE_SEARCH_TERM)
    if not urls:
        raise RuntimeError(
            f"No files matching '{DATAHUB_FILE_SEARCH_TERM}' in project {project_id}."
        )

    response = requests.get(urls[0], timeout=60)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    return Output(
        value=WarehouseTable.from_dataframe(df),
        metadata={
            "scope": "css",
            "row_count": len(df),
            "source_project": DATAHUB_PROJECT_NAME,
            "search_term": DATAHUB_FILE_SEARCH_TERM,
        },
    )


@multi_asset(
    outs={
        "table_a": AssetOut(
            key_prefix=["css", "datahub"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
        "table_b": AssetOut(
            key_prefix=["css", "datahub"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
    },
)
def css_datahub_multi(
    context: AssetExecutionContext,
    datahub: DataHubResource,
):
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    urls = datahub.search_files_from_project(project_id, DATAHUB_FILE_SEARCH_TERM)
    if not urls:
        raise RuntimeError(
            f"No files matching '{DATAHUB_FILE_SEARCH_TERM}' in project {project_id}."
        )

    response = requests.get(urls[0], timeout=60)
    response.raise_for_status()
    _df = pd.read_csv(StringIO(response.text))

    # TODO: derive table_a from _df
    columns_a: tuple[str, ...] = ()
    rows_a: tuple[tuple[str, ...], ...] = ()

    # TODO: derive table_b from _df
    columns_b: tuple[str, ...] = ()
    rows_b: tuple[tuple[str, ...], ...] = ()

    yield Output(
        value=WarehouseTable(name="table_a", columns=columns_a, rows=rows_a),
        output_name="table_a",
        metadata={"row_count": len(rows_a)},
    )
    yield Output(
        value=WarehouseTable(name="table_b", columns=columns_b, rows=rows_b),
        output_name="table_b",
        metadata={"row_count": len(rows_b)},
    )
