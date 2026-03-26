#!/bin/bash
# Initialize local Postgres database for Delta dev
set -euo pipefail

DB_NAME="${POSTGRES_DB:-delta_dev}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-postgres}"
DBT_SCHEMA_RAW="${DBT_SCHEMA_RAW:-src_byod_mitos}"
DBT_SCHEMA_TRANSFORM="${DBT_SCHEMA_TRANSFORM:-rpt_mitos}"
export PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"

for cmd in psql createdb; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Missing required command: $cmd" >&2
        echo "Install PostgreSQL client tools (psql/createdb) and retry." >&2
        exit 1
    fi
done

echo "Checking connection to Postgres at $DB_HOST:$DB_PORT..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" >/dev/null

echo "Ensuring database $DB_NAME exists..."
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | xargs | tr ' ' '\n' | grep -qx "$DB_NAME"; then
    createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
    echo "Created database $DB_NAME"
else
    echo "Database $DB_NAME already exists"
fi

echo "Ensuring schemas $DBT_SCHEMA_RAW and $DBT_SCHEMA_TRANSFORM exist in $DB_NAME..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  -v raw_schema="$DBT_SCHEMA_RAW" \
  -v transform_schema="$DBT_SCHEMA_TRANSFORM" <<'SQL'
CREATE SCHEMA IF NOT EXISTS :"raw_schema";
CREATE SCHEMA IF NOT EXISTS :"transform_schema";
SQL

echo "Database and schemas are ready."
