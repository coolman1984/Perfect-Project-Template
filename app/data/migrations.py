"""Ordered, immutable schema migrations (Constitution Parts 13.1, 16.4, 27.5).

Never change a production schema by hand. Every change is a numbered migration,
applied in order, inside a transaction, and recorded in `sys.schema_migration`
with its checksum.

A migration whose checksum no longer matches what was applied is a hard failure:
editing an applied migration silently gives two databases different shapes while
both claim the same version.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.data.database import Database

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"
FILENAME = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")


class MigrationError(RuntimeError):
    """A migration is missing, out of order, or has been edited after apply."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path

    @property
    def sql(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.sql.encode("utf-8")).hexdigest()


def discover(directory: Path | None = None) -> list[Migration]:
    """Every migration on disk, in version order."""
    directory = directory or MIGRATIONS_DIR
    found: list[Migration] = []
    for path in sorted(directory.glob("*.sql")):
        match = FILENAME.match(path.name)
        if not match:
            raise MigrationError(
                f"{path.name} does not match NNNN_lower_snake_case.sql")
        found.append(Migration(int(match.group(1)), match.group(2), path))

    versions = [m.version for m in found]
    if len(set(versions)) != len(versions):
        raise MigrationError(f"duplicate migration versions: {versions}")
    return found


def applied(database: Database) -> dict[int, str]:
    """{version: checksum} already applied to this database."""
    database.execute(
        "CREATE SCHEMA IF NOT EXISTS sys")
    database.execute("""
        CREATE TABLE IF NOT EXISTS sys.schema_migration (
            version INTEGER PRIMARY KEY, name VARCHAR NOT NULL,
            checksum VARCHAR NOT NULL, applied_at TIMESTAMP NOT NULL,
            application_version VARCHAR)
    """)
    return {row[0]: row[1]
            for row in database.query("SELECT version, checksum FROM sys.schema_migration")}


def migrate(
    database: Database,
    *,
    directory: Path | None = None,
    application_version: str = "0.0.0",
) -> list[int]:
    """Apply every pending migration in order. Returns versions applied."""
    available = discover(directory)
    already = applied(database)

    for migration in available:
        recorded = already.get(migration.version)
        if recorded is not None and recorded != migration.checksum:
            raise MigrationError(
                f"migration {migration.version:04d} ({migration.name}) was edited "
                f"after it was applied. Migrations are immutable — write a new "
                f"one instead (Part 16.4).")

    newly_applied: list[int] = []
    for migration in available:
        if migration.version in already:
            continue
        with database.transaction() as connection:
            connection.execute(migration.sql)
            connection.execute(
                "INSERT INTO sys.schema_migration "
                "(version, name, checksum, applied_at, application_version) "
                "VALUES (?, ?, ?, ?, ?)",
                [migration.version, migration.name, migration.checksum,
                 datetime.now(timezone.utc), application_version],
            )
        newly_applied.append(migration.version)
    return newly_applied
