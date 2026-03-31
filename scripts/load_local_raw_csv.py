#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load a CSV fixture into the local raw Postgres schema for dbt local builds."
    )
    parser.add_argument("--csv", required=True, help="Path to the CSV file to load.")
    parser.add_argument("--table", required=True, help="Destination raw table name.")
    parser.add_argument(
        "--schema",
        default=os.getenv("DBT_SCHEMA_RAW", "src_byod_mitos"),
        help="Destination schema. Defaults to DBT_SCHEMA_RAW or src_byod_mitos.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)

    if not header:
        raise ValueError(f"CSV file {csv_path} is empty or missing a header row")

    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "delta_dev"),
    )

    try:
        with connection, connection.cursor() as cursor:
            column_defs = sql.SQL(", ").join(
                sql.SQL("{} TEXT").format(sql.Identifier(column)) for column in header
            )
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(args.schema))
            )
            cursor.execute(
                sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({})").format(
                    sql.Identifier(args.schema),
                    sql.Identifier(args.table),
                    column_defs,
                )
            )
            cursor.execute(
                sql.SQL("TRUNCATE TABLE {}.{}").format(
                    sql.Identifier(args.schema),
                    sql.Identifier(args.table),
                )
            )

            with csv_path.open(newline="", encoding="utf-8") as handle:
                cursor.copy_expert(
                    sql.SQL("COPY {}.{} ({}) FROM STDIN WITH CSV HEADER")
                    .format(
                        sql.Identifier(args.schema),
                        sql.Identifier(args.table),
                        sql.SQL(", ").join(sql.Identifier(column) for column in header),
                    )
                    .as_string(connection),
                    handle,
                )
    finally:
        connection.close()


if __name__ == "__main__":
    main()
