import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Scope:
    name: str
    dbt_path: str
    raw_schema_env: str
    raw_schema_fallback_env: str | None
    raw_schema_default: str
    transform_schema_env: str
    transform_schema_fallback_env: str | None
    transform_schema_default: str

    def raw_schema(self) -> str:
        if self.raw_schema_fallback_env:
            return os.getenv(
                self.raw_schema_env,
                os.getenv(self.raw_schema_fallback_env, self.raw_schema_default),
            )
        return os.getenv(self.raw_schema_env, self.raw_schema_default)

    def transform_schema(self) -> str:
        if self.transform_schema_fallback_env:
            return os.getenv(
                self.transform_schema_env,
                os.getenv(self.transform_schema_fallback_env, self.transform_schema_default),
            )
        return os.getenv(self.transform_schema_env, self.transform_schema_default)


MITOS_SCOPE = Scope(
    name="mitos",
    dbt_path="models/mitos",
    raw_schema_env="DBT_SCHEMA_MITOS_RAW",
    raw_schema_fallback_env="DBT_SCHEMA_RAW",
    raw_schema_default="src_byod_mitos",
    transform_schema_env="DBT_SCHEMA_MITOS_TRANSFORM",
    transform_schema_fallback_env="DBT_SCHEMA_TRANSFORM",
    transform_schema_default="rpt_mitos",
)

CORE_SCOPE = Scope(
    name="core",
    dbt_path="models/core",
    raw_schema_env="DBT_SCHEMA_CORE_RAW",
    raw_schema_fallback_env="DBT_SCHEMA_RAW",
    raw_schema_default="src_byod_core",
    transform_schema_env="DBT_SCHEMA_CORE_TRANSFORM",
    transform_schema_fallback_env="DBT_SCHEMA_TRANSFORM",
    transform_schema_default="rpt_core",
)

CSS_SCOPE = Scope(
    name="css",
    dbt_path="models/css",
    raw_schema_env="DBT_SCHEMA_CSS_RAW",
    raw_schema_fallback_env=None,
    raw_schema_default="src_byod_css",
    transform_schema_env="DBT_SCHEMA_CSS_TRANSFORM",
    transform_schema_fallback_env=None,
    transform_schema_default="rpt_css",
)

SHARED_SCOPE_NAMES = ("shared",)
