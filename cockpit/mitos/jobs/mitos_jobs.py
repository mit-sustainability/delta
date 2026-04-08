from dagster import AssetSelection, define_asset_job

mitos_job = define_asset_job("mitos_job", selection=AssetSelection.groups("mitos"))

__all__ = ["mitos_job"]
