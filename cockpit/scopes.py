import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Scope:
    name: str
    dbt_path: str
    raw_schema_env: str
    raw_schema_fallback_envs: tuple[str, ...]
    raw_schema_default: str
    transform_schema_env: str
    transform_schema_fallback_envs: tuple[str, ...]
    transform_schema_default: str

    def raw_schema(self) -> str:
        return self._resolve(
            self.raw_schema_env, self.raw_schema_fallback_envs, self.raw_schema_default
        )

    def transform_schema(self) -> str:
        return self._resolve(
            self.transform_schema_env,
            self.transform_schema_fallback_envs,
            self.transform_schema_default,
        )

    @property
    def dbt_selector(self) -> str:
        return f"tag:domain:{self.name}"

    def _resolve(self, primary: str, fallbacks: tuple[str, ...], default: str) -> str:
        for env in (primary, *fallbacks):
            value = os.getenv(env)
            if value:
                return value
        return default


MITOS_SCOPE = Scope(
    name="mitos",
    dbt_path="models/mitos",
    raw_schema_env="DBT_SCHEMA_MITOS_RAW",
    raw_schema_fallback_envs=("DBT_SCHEMA_RAW",),
    raw_schema_default="src_byod_mitos",
    transform_schema_env="DBT_SCHEMA_MITOS_TRANSFORM",
    transform_schema_fallback_envs=("DBT_SCHEMA_TRANSFORM",),
    transform_schema_default="rpt_mitos",
)

CORE_SCOPE = Scope(
    name="core",
    dbt_path="models/core",
    raw_schema_env="DBT_SCHEMA_CORE_RAW",
    raw_schema_fallback_envs=("DBT_SCHEMA_MITOS_RAW", "DBT_SCHEMA_RAW"),
    raw_schema_default="src_byod_core",
    transform_schema_env="DBT_SCHEMA_CORE_TRANSFORM",
    transform_schema_fallback_envs=("DBT_SCHEMA_MITOS_TRANSFORM", "DBT_SCHEMA_TRANSFORM"),
    transform_schema_default="rpt_core",
)

CSS_SCOPE = Scope(
    name="css",
    dbt_path="models/css",
    raw_schema_env="DBT_SCHEMA_CSS_RAW",
    raw_schema_fallback_envs=("DBT_SCHEMA_RAW",),
    raw_schema_default="src_byod_css",
    transform_schema_env="DBT_SCHEMA_CSS_TRANSFORM",
    transform_schema_fallback_envs=("DBT_SCHEMA_TRANSFORM",),
    transform_schema_default="rpt_css",
)

SHARED_SCOPE_NAMES = ("shared",)
