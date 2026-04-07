# Quickstart: MITOS/CSS Domain Structure

## 1) Create domain-aware folder layout

1. Organize Dagster orchestration under `cockpit/` by shared concerns and scope:
   - `shared/` for resources, schedules, sensors, and shared tests
   - `core/` for shared Python-managed assets/jobs/tests
   - `mitos/` for MITOS-owned assets/jobs/tests
   - `css/` for CSS-owned assets/jobs/tests
2. Add dbt domain folders under `dbt/models/`:
   - `mitos/raw`, `mitos/staging`, `mitos/final`
   - `css/raw`, `css/staging`, `css/final`

## 2) Wire Dagster grouping and jobs

1. Ensure each asset carries domain-aligned group metadata.
2. Register domain-focused jobs (at minimum `mitos` and `css` selections).
3. Keep shared Python-managed assets under `core` and include them intentionally.

## 3) Wire dbt domain selection

1. Update `dbt_project.yml` model configs for domain paths/tags.
2. Add `selectors.yml` for stable commands such as:
   - `dbt build --selector mitos`
   - `dbt build --selector css`
3. Keep dbt orchestration in Dagster thin: `DbtCliResource` launches dbt, while dbt remains the source of truth for model schemas/materializations.

## 4) Wire Python asset IO managers

1. Use stable logical IO manager keys such as `raw_io_manager` in Python-managed asset decorators.
2. Bind those keys from the owning `defs.py` using scope metadata and environment-specific Postgres/Snowflake IO manager builders.
3. Keep Postgres/Snowflake connection resources separate from Dagster IO manager implementations.

## 5) Verify dual-target behavior

1. Run local domain build checks:
   - `DBT_TARGET=local dbt build --selector mitos`
   - `DBT_TARGET=local dbt build --selector css`
2. Run prod domain build checks:
   - `DBT_TARGET=prod dbt build --selector mitos`
   - `DBT_TARGET=prod dbt build --selector css`
3. Run orchestration tests/definitions checks for domain registration.

## 6) Incremental migration guardrails

1. Keep MITOS defaults while introducing CSS.
2. Move assets/models domain-by-domain; avoid mixed ownership files.
3. Remove transitional defaults once both domains have explicit runtime selection.
