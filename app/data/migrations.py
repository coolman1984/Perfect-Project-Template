"""Ordered, immutable schema migrations.

Core project execution can stop at the reusable system migration while legacy
reference executors may still apply their compatibility migrations. `max_version`
is intentionally explicit so a project-centric run never needs report-specific
reference tables merely to obtain sys/quality/checkpoint infrastructure.
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
    pass


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
    directory = directory or MIGRATIONS_DIR
    found: list[Migration] = []
    for path in sorted(directory.glob("*.sql")):
        match = FILENAME.match(path.name)
        if not match:
            raise MigrationError(
                f"{path.name} does not match NNNN_lower_snake_case.sql")
        found.append(Migration(int(match.group(1)), match.group(2), path))
    versions = [migration.version for migration in found]
    if len(set(versions)) != len(versions):
        raise MigrationError(f"duplicate migration versions: {versions}")
    return found


def applied(database: Database) -> dict[int, str]:
    database.execute("CREATE SCHEMA IF NOT EXISTS sys")
    database.execute("""
        CREATE TABLE IF NOT EXISTS sys.schema_migration (
            version INTEGER PRIMARY KEY, name VARCHAR NOT NULL,
            checksum VARCHAR NOT NULL, applied_at TIMESTAMP NOT NULL,
            application_version VARCHAR)
    """)
    return {
        row[0]: row[1]
        for row in database.query(
            "SELECT version, checksum FROM sys.schema_migration")
    }


def migrate(
    database: Database,
    *,
    directory: Path | None = None,
    application_version: str = "0.0.0",
    max_version: int | None = None,
) -> list[int]:
    available = discover(directory)
    if max_version is not None:
        available = [m for m in available if m.version <= max_version]
    already = applied(database)
    for migration in available:
        recorded = already.get(migration.version)
        if recorded is not None and recorded != migration.checksum:
            raise MigrationError(
                f"migration {migration.version:04d} ({migration.name}) was "
                "edited after apply; migrations are immutable")
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
