# Delta Project

Delta is the evolution of the `basin` data platform, migrated to use **Snowflake** as the backend.

## Architecture

This is a monorepo that contains:
1. **`dbt/`**: Data transformations, modeling, and query management, driven by `dbt-snowflake`. Warehouse schemas follow `raw`, `staging`, and `final`.
2. **`cockpit/`**: The Dagster orchestration layer that parses the dbt manifest and triggers jobs on schedules/sensors.
3. **`notebooks/`**: Directory intended for git sync with Snowflake UI-generated Notebooks.

## Snowflake UI Notebook Integration

To use Snowflake Git integration for notebooks:
1. Setup a Git API integration in Snowflake linked to this repository.
2. Link your Snowflake Notebook to this repository under the `notebooks/` directory.
3. Your Snowflake Notebooks can be pushed from the Snowflake UI directly into the `notebooks` folder, allowing them to be version controlled alongside your Dagster orchestrator and dbt models.

## Local Development

```bash
# 1. Install dependencies in a Python 3.13 environment
uv sync --python 3.13

# 2. Initialize local development database + schemas on Postgres (default: localhost:5432)
make init-db

# 3. Build dbt dependencies and run the local target
cd dbt
dbt deps
DBT_TARGET=local dbt build

# 4. Start Dagster local development server
cd ..
dagster dev
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

If you prefer browser-based authentication locally, leave `SNOWFLAKE_PASSWORD` unset and keep `SNOWFLAKE_AUTHENTICATOR` unset or set it to `externalbrowser`.

For convenience, you can also use:

```bash
make dbt-build-local
make dbt-build-prod
```

## Local Raw Source Fixtures

If a dbt model depends on a raw table that normally lands in Snowflake, keep the dbt model pointed
at a logical `source()` and mirror that source into local Postgres for `DBT_TARGET=local`.

1. Declare the raw table as a dbt source in `dbt/models/schema.yml`.
2. Load a representative CSV fixture into local Postgres:

```bash
make load-local-raw RAW_CSV_PATH=./path/to/uploaded_table.csv RAW_TABLE=uploaded_table_example
```

The loader creates the table in `DBT_SCHEMA_RAW`, loads all columns as `TEXT`, and replaces its
contents on each run. Downstream staging models should cast types explicitly, which keeps the local
fixture flow simple and stable.

## Dagster Warehouse Resource Pattern

For Dagster raw-processing assets, use the shared `warehouse` resource in
`cockpit/definitions.py`. It switches between:

- `local`: PostgreSQL, for local or test runs
- `prod`: Snowflake, for target-state production runs

Selection is driven by `WAREHOUSE_TARGET`, falling back to `DBT_TARGET`.

This is the right pattern when the same asset logic needs to write raw tables in both environments
without hardcoding a backend-specific client at the asset call site.
