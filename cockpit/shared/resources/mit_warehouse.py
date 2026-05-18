import os
from contextlib import contextmanager
from typing import Iterator

import oracledb
from dagster import ConfigurableResource, get_dagster_logger
from oracledb import DatabaseError

logger = get_dagster_logger()

# oracledb.init_oracle_client may only be called once per process
_oracle_client_initialized = False


def _ensure_oracle_client() -> None:
    global _oracle_client_initialized
    if _oracle_client_initialized:
        return
    # thick mode required — MIT Warehouse enforces Oracle Native Network Encryption
    if os.getenv("DBT_TARGET", "local") == "local":
        lib_dir = os.getenv("ORACLE_CLIENT_LIB_DIR", "/opt/oracle/instantclient_23_26")
        oracledb.init_oracle_client(lib_dir=lib_dir)
    else:
        oracledb.init_oracle_client()
    _oracle_client_initialized = True


class MITWarehouseResource(ConfigurableResource):
    """Dagster resource for read-only access to the MIT Oracle Data Warehouse."""

    def _connection_config(self) -> dict[str, str | int]:
        return {
            "user": os.getenv("MIT_WHRS_USER", ""),
            "password": os.getenv("MIT_WHRS_PASSWORD", ""),
            "host": os.getenv("MIT_WHRS_HOST", "warehouse.mit.edu"),
            "port": int(os.getenv("MIT_WHRS_PORT", "1521")),
            "sid": os.getenv("MIT_WHRS_SID", "DWRHS"),
        }

    @contextmanager
    def connect(self) -> Iterator[oracledb.Connection]:
        _ensure_oracle_client()
        cfg = self._connection_config()
        conn = oracledb.connect(
            user=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            sid=cfg["sid"],
        )
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, arraysize: int = 1000) -> list[tuple]:
        """Run a read-only query and return all rows as a list of tuples."""
        try:
            with self.connect() as conn:
                logger.info("Connected to MIT Data Warehouse")
                with conn.cursor() as cursor:
                    cursor.arraysize = arraysize
                    cursor.execute(query)
                    return cursor.fetchall()
        except DatabaseError as e:
            logger.error(f"MIT Warehouse query failed: {e}")
            return []
