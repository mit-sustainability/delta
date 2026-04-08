from dagster import AssetSelection, define_asset_job

css_job = define_asset_job("css_job", selection=AssetSelection.groups("css"))

__all__ = ["css_job"]
