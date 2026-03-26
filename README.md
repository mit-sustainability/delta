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
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Initialize local dev database + schemas on your existing local Postgres (default: localhost:5432)
make init-db

# 3. Build dbt manifest (if not automatically handled)
cd dbt
dbt deps

# 4. Start Dagster local development server
cd ..
dagster dev
```

## Environment Targets

`dbt/profiles.yml` already maps targets as:
- `dev` -> PostgreSQL (local, from `POSTGRES_*` env vars)
- `prod` -> Snowflake (from `SNOWFLAKE_*` env vars)

Use `.envrc` for local defaults:
- `DBT_TARGET=dev`
- `POSTGRES_PORT=5432`

Switch to production runs explicitly:

```bash
export DBT_TARGET=prod
export SNOWFLAKE_ACCOUNT=...
export SNOWFLAKE_USER=...
export SNOWFLAKE_PASSWORD=...
export SNOWFLAKE_ROLE=...
export SNOWFLAKE_DATABASE=...
export SNOWFLAKE_WAREHOUSE=...
```

Then run `dbt build` (or Dagster Snowflake assets) against Snowflake.
