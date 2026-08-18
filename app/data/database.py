"""DuckDB connection and transaction policy (Constitution Parts 13.2, 23.3).

DuckDB is the brain: one embedded file, no server, fast analytical SQL. This
module owns connection policy so no other layer opens its own writer.

Operating rules enforced here (Part 23.3):
  * one coordinated writer per database file
  * extension autoinstall/autoload DISABLED — a runtime extension download is a
    forbidden network call (Part 23.6)
  * memory_limit / temp_directory / threads configured from settings
  * schemas kept separate: sys, raw, clean, quality, analytics
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

SCHEMAS = ("sys", "raw", "clean", "quality", "analytics")


class Database:
    """A single coordinated DuckDB writer.

    Use as a context manager so the connection always closes and a failed
    transaction always rolls back — trusted history must survive any failure
    (rule 9).
    """

    def __init__(
        self,
        path: str | Path,
        *,
        memory_limit: str = "1GB",
        threads: int = 2,
        temp_directory: str | Path | None = None,
        read_only: bool = False,
    ) -> None:
        self.path = Path(path)
        self._memory_limit = memory_limit
        self._threads = threads
        self._temp_directory = Path(temp_directory) if temp_directory else None
        self._read_only = read_only
        self._connection: Any = None

    # -- lifecycle ---------------------------------------------------------

    def connect(self) -> Any:
        import duckdb  # imported lazily so the tool tier never needs it

        if self._connection is not None:
            return self._connection

        if not self._read_only:
            self.path.parent.mkdir(parents=True, exist_ok=True)

        connection = duckdb.connect(str(self.path), read_only=self._read_only)

        # Part 23.6: the application must never fetch an extension at runtime.
        connection.execute("SET autoinstall_known_extensions = false")
        connection.execute("SET autoload_known_extensions = false")
        connection.execute(f"SET memory_limit = '{self._memory_limit}'")
        connection.execute(f"SET threads = {int(self._threads)}")
        if self._temp_directory is not None:
            self._temp_directory.mkdir(parents=True, exist_ok=True)
            connection.execute(f"SET temp_directory = '{self._temp_directory}'")

        self._connection = connection
        if not self._read_only:
            self._ensure_schemas()
        return connection

    def _ensure_schemas(self) -> None:
        for schema in SCHEMAS:
            self._connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> Database:
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- queries -----------------------------------------------------------

    def execute(self, sql: str, parameters: object = None) -> Any:
        connection = self.connect()
        return connection.execute(sql, parameters) if parameters else connection.execute(sql)

    def query(self, sql: str, parameters: object = None) -> list[tuple]:
        return self.execute(sql, parameters).fetchall()

    def scalar(self, sql: str, parameters: object = None) -> Any:
        row = self.execute(sql, parameters).fetchone()
        return None if row is None else row[0]

    def columns_of(self, qualified_table: str) -> list[str]:
        """Column names for a `schema.table`, in ordinal order.

        `PRAGMA table_info` does not accept a schema-qualified name, so asking
        it for "raw.production" silently looks for a table called "production"
        in the default schema. information_schema is unambiguous.
        """
        if "." in qualified_table:
            schema, table = qualified_table.split(".", 1)
        else:
            schema, table = "main", qualified_table
        return [row[0] for row in self.query(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = ? AND table_name = ? ORDER BY ordinal_position",
            [schema, table])]

    @contextlib.contextmanager
    def transaction(self) -> Iterator[Any]:
        """All-or-nothing. On any failure the history is left exactly as it was.

        This is the Part 8.5 safe-commit boundary: validate, update, insert,
        apply deletions, reconcile — then COMMIT. Any exception rolls back.
        """
        connection = self.connect()
        connection.execute("BEGIN TRANSACTION")
        try:
            yield connection
        except Exception:
            connection.execute("ROLLBACK")
            raise
        connection.execute("COMMIT")
