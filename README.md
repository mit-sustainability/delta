# Delta Project

Delta is the evolution of the `basin` data platform, migrated to use **Snowflake** as the backend.

## Architecture

This is a monorepo that contains:
1. **`dbt/`**: Data transformations, modeling, and query management, driven by `dbt-snowflake`. Warehouse schemas follow `raw`, `staging`, and `final`.
2. **`cockpit/`**: The Dagster orchestration layer, organized by shared concerns and scope packages:
   - `cockpit/shared/`: shared resources, dbt wiring, IO managers, schedules, sensors
   - `cockpit/core/`: shared Python-managed assets and jobs
   - `cockpit/mitos/`: MITOS-owned orchestration code
   - `cockpit/css/`: CSS-owned orchestration code
3. **`notebooks/`**: Directory intended for git sync with Snowflake UI-generated Notebooks.

## Snowflake UI Notebook Integration

To use Snowflake Git integration for notebooks:
1. Setup a Git API integration in Snowflake linked to this repository.
2. Link your Snowflake Notebook to this repository under the `notebooks/` directory.
3. Your Snowflake Notebooks can be pushed from the Snowflake UI directly into the `notebooks` folder, allowing them to be version controlled alongside your Dagster orchestrator and dbt models.

## Local Development

```bash
# 1. Install runtime and dev dependencies in a Python 3.13 environment
uv sync --python 3.13 --extra dev

# 2. Install git hooks for local checks
uv run pre-commit install

# 3. Initialize local development database + schemas on Postgres (default: localhost:5432)
make init-db

# 4. Build dbt dependencies and run the local target
cd dbt
dbt deps
DBT_TARGET=local dbt build

# 5. Start Dagster local development server
cd ..
uv run dg dev
```

To run the configured hooks manually without creating a commit:

```bash
uv run pre-commit run --all-files
```

## Environment Targets

`dbt/profiles.yml` already maps targets as:
- `local` -> PostgreSQL (local or test, from `POSTGRES_*` env vars)
- `prod` -> Snowflake (from `SNOWFLAKE_*` env vars)

Use `.envrc` for local defaults:
- `DBT_TARGET=local`
- `POSTGRES_PORT=5432`

Switch targets explicitly:

```bash
export DBT_TARGET=local
dbt build
```

```bash
export DBT_TARGET=prod
export SNOWFLAKE_ACCOUNT=...
export SNOWFLAKE_USER=...
export SNOWFLAKE_ROLE=...
export SNOWFLAKE_DATABASE=...
export SNOWFLAKE_WAREHOUSE=...
```

If you want password authentication for non-interactive production runs, add:

```bash
export SNOWFLAKE_PASSWORD=...
export SNOWFLAKE_AUTHENTICATOR=snowflake
```

For deployed EC2 Dagster or other unattended runs, prefer Snowflake key-pair auth instead of
`externalbrowser`:

```bash
export SNOWFLAKE_PRIVATE_KEY_PATH=/run/secrets/snowflake_service_user.p8
export SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=...
unset SNOWFLAKE_AUTHENTICATOR
```

If you prefer browser-based authentication locally, leave `SNOWFLAKE_PASSWORD` unset and keep `SNOWFLAKE_AUTHENTICATOR` unset or set it to `externalbrowser`.

For convenience, you can also use:

```bash
make dbt-build-local
make dbt-build-prod
```

## Local Raw Source Fixtures

If a dbt model depends on a raw table that normally lands in Snowflake, keep the dbt model pointed
at a logical `source()` and mirror that source into local Postgres for `DBT_TARGET=local`.

1. Declare the upstream table as a dbt source in the owning domain `sources.yml`.
2. Point that source at either an external Snowflake schema or a local mirrored Postgres schema via env vars.
3. Load a representative CSV fixture into local Postgres when you want local `DBT_TARGET=local` builds:

```bash
make load-local-raw RAW_CSV_PATH=./path/to/uploaded_table.csv RAW_TABLE=uploaded_table_example
```

Optionally choose the target mirror schema explicitly:

```bash
make load-local-raw RAW_CSV_PATH=./path/to/uploaded_table.csv RAW_TABLE=uploaded_table_example RAW_SCHEMA=src_external_ops_local
```

The loader creates the table in the requested schema, loads all columns as `TEXT`, and replaces its
contents on each run. Downstream staging models should cast types explicitly, which keeps the local
fixture flow simple and stable. Source schemas can be switched per source contract with env vars such
as `MITOS_RAW_UPLOADS_SOURCE_SCHEMA`, `MITOS_WAREHOUSE_SMOKE_SOURCE_SCHEMA`, or
`CSS_RAW_UPLOADS_SOURCE_SCHEMA`.

## Dagster Warehouse IO Manager Pattern

For Python-managed Dagster warehouse assets, use a stable logical IO manager key in the asset
definition, then bind that key from the owning `defs.py`.

At runtime the binding switches between:

- `local`: a Postgres IO manager
- `prod`: a Snowflake IO manager

Selection is driven by `WAREHOUSE_TARGET`, falling back to `DBT_TARGET`, via
`build_warehouse_io_manager(...)` in `cockpit/shared/resources/io_managers.py`.

This keeps asset code backend-agnostic: the asset declares a logical key such as
`raw_io_manager`, while the scope `defs.py` chooses the environment-specific implementation and
schema.

## Warehouse Smoke Test Path

The repository now includes a deterministic core Dagster raw asset,
`cockpit.core.assets.warehouse_test_input`, that writes a small table named
`warehouse_test_input` through the logical `raw_io_manager`. A dbt staging/final path can then
build on top of that raw table.

Run the local smoke path:

```bash
make init-db
uv run python -c "from cockpit.core.assets import warehouse_test_input; from dagster import materialize; from cockpit.shared.resources import build_warehouse_io_manager; materialize([warehouse_test_input], resources={'raw_io_manager': build_warehouse_io_manager('local', 'src_byod_core')})"
cd dbt && DBT_TARGET=local uv run dbt build --select stg_test_asset fct_test_asset_summary
```

Run the Snowflake smoke path against a pre-created schema:

```bash
export WAREHOUSE_TARGET=prod
uv run python -c "from cockpit.core.assets import warehouse_test_input; from dagster import materialize; from cockpit.shared.resources import build_warehouse_io_manager; materialize([warehouse_test_input], resources={'raw_io_manager': build_warehouse_io_manager('prod', 'src_byod_core')})"
cd dbt && DBT_TARGET=prod uv run dbt build --select stg_test_asset fct_test_asset_summary
```

Snowflake production runs assume the target schemas already exist and are
granted to the service role. The smoke asset may replace the test table inside that schema, but it
does not attempt to create the schema in Snowflake.

## Automated Verification Coverage

Recent smoke-path changes have automated unit coverage in scope-local test folders:

- `cockpit/shared/tests/test_resources.py` validates Postgres and Snowflake resource configuration,
  IO manager selection, and top-level Definitions wiring.
- `cockpit/core/tests/test_core_assets.py` validates that `warehouse_test_input` emits the expected
  warehouse payload and that the Postgres/Snowflake IO managers write the correct SQL.
- `cockpit/core/tests/test_core_jobs.py`, `cockpit/mitos/tests/test_mitos_jobs.py`, and
  `cockpit/css/tests/test_css_jobs.py` validate scope job registration.

Run the suite with:

```bash
uv run pytest -q
```
