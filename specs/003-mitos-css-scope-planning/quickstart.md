# Quickstart: MITOS/CSS Domain Structure

## 1) Create domain-aware folder layout

1. Add Dagster domain folders under `cockpit/assets/`:
   - `shared/`
   - `mitos/`
   - `css/`
2. Add dbt domain folders under `dbt/models/`:
   - `shared/`
   - `mitos/raw`, `mitos/staging`, `mitos/final`
   - `css/raw`, `css/staging`, `css/final`

## 2) Wire Dagster grouping and jobs

1. Ensure each asset carries domain-aligned group metadata.
2. Register domain-focused jobs (at minimum `mitos` and `css` selections).
3. Keep shared assets grouped as `shared` and included intentionally.

## 3) Wire dbt domain selection

1. Update `dbt_project.yml` model configs for domain paths/tags.
2. Add `selectors.yml` for stable commands such as:
   - `dbt build --selector mitos`
   - `dbt build --selector css`
3. Keep shared macros in shared macro paths.

## 4) Verify dual-target behavior

1. Run local domain build checks:
   - `DBT_TARGET=local dbt build --selector mitos`
   - `DBT_TARGET=local dbt build --selector css`
2. Run prod domain build checks:
   - `DBT_TARGET=prod dbt build --selector mitos`
   - `DBT_TARGET=prod dbt build --selector css`
3. Run orchestration tests/definitions checks for domain registration.

## 5) Incremental migration guardrails

1. Keep MITOS defaults while introducing CSS.
2. Move assets/models domain-by-domain; avoid mixed ownership files.
3. Remove transitional defaults once both domains have explicit runtime selection.
