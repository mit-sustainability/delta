import io

import pandas as pd
import requests
from dagster import AssetExecutionContext, AssetOut, Output, asset, multi_asset

from ...shared.resources import WarehouseTable
from ...shared.resources.datahub import DataHubResource
from ...shared.utils import normalize_column_name

DATAHUB_PROJECT_NAME = "Utility Rate-setting"


@multi_asset(
    outs={
        "electricity_consumption_pi": AssetOut(
            key_prefix=["css", "rate"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
        "electricity_production_report": AssetOut(
            key_prefix=["css", "rate"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
    },
)
def electricity_residuals(
    context: AssetExecutionContext,
    datahub: DataHubResource,
):
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    download_links = datahub.search_files_from_project(project_id, "Detail of Electrical residuals")
    if not download_links:
        raise RuntimeError(
            f"No files matching 'Detail of Electrical residuals' in project {project_id}."
        )

    workbook = pd.ExcelFile(download_links[0], engine="openpyxl")
    # Load consumption sheet
    ele_res = pd.read_excel(workbook, sheet_name=1, skiprows=4)
    ele_res.columns = ele_res.columns.str.rstrip()
    ele_res = ele_res[["Square feet", "Bldg #", "SAP", "ADJUSTED METERS"]].iloc[:-1].copy()
    ele_res["Bldg"] = ele_res["Bldg #"].fillna(ele_res["Square feet"])
    ele_res.columns = [normalize_column_name(col) for col in ele_res.columns]

    sel_col_res = [
        "bldg",
        "adjusted_meters",
        "sap",
    ]
    ele_res = ele_res[sel_col_res]
    ## Load production sheet
    ele_prod = pd.read_excel(
        workbook,
        sheet_name=0,
        skiprows=0,
        nrows=15,
        usecols="C,U",
        names=["item", "amount"],
    )

    yield Output(
        value=WarehouseTable.from_dataframe(ele_res),
        output_name="electricity_consumption_pi",
        metadata={"row_count": len(ele_res)},
    )
    yield Output(
        value=WarehouseTable.from_dataframe(ele_prod),
        output_name="electricity_production_report",
        metadata={"row_count": len(ele_prod)},
    )


@multi_asset(
    outs={
        "steam_consumption_pi": AssetOut(
            key_prefix=["css", "rate"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
        "steam_production_report": AssetOut(
            key_prefix=["css", "rate"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
    },
)
def steam_residuals(
    context: AssetExecutionContext,
    datahub: DataHubResource,
):
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    download_links = datahub.search_files_from_project(
        project_id, "Detail of Steam Usage Residual", tags=["CUP", "steam"]
    )
    if not download_links:
        raise RuntimeError(f"No files matching steam/chilled water in project {project_id}.")

    workbook = pd.ExcelFile(download_links[0], engine="openpyxl")

    # Load steam consumption sheet
    steam_res = pd.read_excel(workbook, sheet_name=1)
    steam_res.columns = steam_res.columns.str.rstrip()
    steam_res = (
        steam_res[["Receiver Cost Center", "Bldg #", "Steam consumption Adjusted"]].iloc[:-5].copy()
    )
    steam_res.columns = [normalize_column_name(col) for col in steam_res.columns]

    # Load steam production sheet
    steam_prod = pd.read_excel(
        workbook,
        sheet_name=0,
        skiprows=0,
        nrows=14,
        usecols="C,U",
        names=["item", "amount"],
    )
    steam_prod.columns = steam_prod.columns.str.rstrip()
    steam_prod.columns = [normalize_column_name(col) for col in steam_prod.columns]

    yield Output(
        value=WarehouseTable.from_dataframe(steam_res),
        output_name="steam_consumption_pi",
        metadata={"row_count": len(steam_res)},
    )
    yield Output(
        value=WarehouseTable.from_dataframe(steam_prod),
        output_name="steam_production_report",
        metadata={"row_count": len(steam_prod)},
    )


@multi_asset(
    outs={
        "chilled_water_consumption_pi": AssetOut(
            key_prefix=["css", "rate"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
        "chilled_water_production_report": AssetOut(
            key_prefix=["css", "rate"],
            group_name="css",
            tags={"layer": "raw"},
            io_manager_key="css_raw_io_manager",
        ),
    },
)
def chilled_water_residuals(
    context: AssetExecutionContext,
    datahub: DataHubResource,
):
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    download_links = datahub.search_files_from_project(
        project_id, "Detail of Chilled Water Usage Residual", tags=["CUP", "chilled"]
    )
    if not download_links:
        raise RuntimeError(f"No files matching steam/chilled water in project {project_id}.")

    workbook = pd.ExcelFile(download_links[0], engine="openpyxl")

    # Chilled water consumption sheet
    chilled_res = pd.read_excel(workbook, sheet_name=1, skiprows=1)
    chilled_res.columns = chilled_res.columns.str.rstrip()
    chilled_res = chilled_res[["Receiver Cost Center", "Bldg #", "Adjusted Usage"]].iloc[:-1].copy()
    chilled_res.columns = [normalize_column_name(col) for col in chilled_res.columns]

    # Load chilled water production sheet
    chilled_prod = pd.read_excel(
        workbook,
        sheet_name=0,
        skiprows=0,
        nrows=6,
        usecols="C,U",
        names=["item", "amount"],
    )
    chilled_prod.columns = chilled_prod.columns.str.rstrip()
    chilled_prod.columns = [normalize_column_name(col) for col in chilled_prod.columns]

    yield Output(
        value=WarehouseTable.from_dataframe(chilled_res),
        output_name="chilled_water_consumption_pi",
        metadata={"row_count": len(chilled_res)},
    )
    yield Output(
        value=WarehouseTable.from_dataframe(chilled_prod),
        output_name="chilled_water_production_report",
        metadata={"row_count": len(chilled_prod)},
    )


@asset(
    key_prefix=["css", "rate"],
    group_name="css",
    tags={"layer": "raw"},
    io_manager_key="css_raw_io_manager",
)
def assumed_rate(
    context: AssetExecutionContext,
    datahub: DataHubResource,
) -> Output[WarehouseTable]:
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    download_links = datahub.search_files_from_project(project_id, "assumed_rate.csv")
    if not download_links:
        raise RuntimeError(f"No file matching 'assumed_rate.csv' in project {project_id}.")

    response = requests.get(download_links[0], timeout=60)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))

    return Output(
        value=WarehouseTable.from_dataframe(df),
        metadata={"row_count": len(df)},
    )


@asset(
    key_prefix=["css", "rate"],
    group_name="css",
    tags={"layer": "raw"},
    io_manager_key="css_raw_io_manager",
)
def mthw_consumption_pi(
    context: AssetExecutionContext,
    datahub: DataHubResource,
) -> Output[WarehouseTable]:
    project_id = datahub.get_project_id(DATAHUB_PROJECT_NAME)
    if not project_id:
        raise RuntimeError(f"DataHub project '{DATAHUB_PROJECT_NAME}' not found.")

    download_links = datahub.search_files_from_project(
        project_id, "2026-03 All Utilities (Used for MTHW Totals)", tags=["pi"]
    )
    if not download_links:
        raise RuntimeError(f"No files matching MTHW in project {project_id}.")

    workbook = pd.ExcelFile(download_links[0], engine="openpyxl")
    mthw_res = pd.read_excel(workbook, sheet_name=3, skiprows=14)
    mthw_res.columns = mthw_res.columns.str.rstrip()
    mthw_res = (
        mthw_res[
            [
                "Bldg #",
                "Receiver Cost Center",
                "Metered Usage - MMBTU",
                "Final Bill - kbtu",
            ]
        ]
        .iloc[:-1]
        .copy()
    )
    mthw_res.columns = [normalize_column_name(col) for col in mthw_res.columns]

    return Output(
        value=WarehouseTable.from_dataframe(mthw_res),
        metadata={"row_count": len(mthw_res)},
    )
