"""Project-owned schema migrations (V10 Part 15).

`app/data/migrations.py` is the reusable engine's own migration ledger: it
creates `sys.run`, `quality.*`, `sys.checkpoint` and the legacy reference
tables, tracked in `sys.schema_migration`. That ledger is Universal Core and a
normal project must never carry a `sql/history.sql` or otherwise reach into it
(PROJECT_SKILL.md Part 8).

A project's *own* schema evolves independently: a new business column, a
renamed source, a corrected type. This module is where that change goes —
`projects/<project_id>/migrations/NNNN_name.sql` — tracked in its own ledger
table so a project's migration numbering never collides with another
project's, or with the engine's.

Rules carried over unchanged from the engine ledger, because a second set of
looser rules for "just the project" would be exactly the kind of duplicated
history mechanism V10 Part 8 forbids:

- migrations are ordered, immutable once applied, and checksummed;
- each runs inside its own transaction, so a failed migration leaves the
  previous schema and trusted data exactly as they were;
- schema and project_version stay aligned per project.

Ordering with `ProjectPipeline.prepare()` is three phases, in order:
`_create_source_tables` (`CREATE TABLE IF NOT EXISTS` from *current*
`sources.toml`), then this module's `migrate()`, then `_validate_source_schema`
(configuration must now match the database exactly). A genuinely fresh project
database gets its full current shape from phase one with no migration doing
real work; a migration only does real work against a database left over from
an older configuration. Because phase one always runs first, a migration that
alters an already-current table must be self-guarding —
`ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`, matching the same idempotence
the engine's own `CREATE TABLE IF NOT EXISTS` already relies on — not merely
"runs once". Ordering migrations before phase one instead would break the
fresh-database case outright: `ALTER TABLE` fails on a table that does not
exist yet.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.data.database import Database

FILENAME = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")


class ProjectMigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProjectMigration:
    version: int
    name: str
    path: Path

    @property
    def sql(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.sql.encode("utf-8")).hexdigest()


def discover(migrations_dir: Path) -> list[ProjectMigration]:
    """A project with no migrations directory has simply never needed one."""
    if not migrations_dir.is_dir():
        return []
    found: list[ProjectMigration] = []
    for path in sorted(migrations_dir.glob("*.sql")):
        match = FILENAME.match(path.name)
        if not match:
            raise ProjectMigrationError(
                f"{path.name} does not match NNNN_lower_snake_case.sql "
                f"(project migrations use the same ordered-immutable naming "
                f"as engine migrations)")
        found.append(ProjectMigration(int(match.group(1)), match.group(2), path))
    versions = [migration.version for migration in found]
    if len(set(versions)) != len(versions):
        raise ProjectMigrationError(
            f"duplicate project migration versions: {versions}")
    return found


def applied(database: Database, *, project_id: str) -> dict[int, str]:
    database.execute("CREATE SCHEMA IF NOT EXISTS sys")
    database.execute("""
        CREATE TABLE IF NOT EXISTS sys.project_schema_migration (
            project_id           VARCHAR NOT NULL,
            version               INTEGER NOT NULL,
            name                  VARCHAR NOT NULL,
            checksum              VARCHAR NOT NULL,
            applied_at            TIMESTAMP NOT NULL,
            application_version   VARCHAR,
            PRIMARY KEY (project_id, version)
        )
    """)
    return {
        row[0]: row[1]
        for row in database.query(
            "SELECT version, checksum FROM sys.project_schema_migration "
            "WHERE project_id = ?", [project_id])
    }


def migrate(
    database: Database,
    *,
    project_id: str,
    migrations_dir: Path,
    application_version: str = "0.0.0",
) -> list[int]:
    """Apply every not-yet-applied project migration, oldest first.

    Raises before touching the database if any previously applied migration's
    file content no longer matches its recorded checksum (Part 15: "schema
    drift never silently changes trusted tables"). Each new migration commits
    in its own transaction, so a failure partway through a multi-migration
    catch-up leaves every already-applied migration intact and stops there.
    """
    available = discover(migrations_dir)
    already = applied(database, project_id=project_id)
    for migration in available:
        recorded = already.get(migration.version)
        if recorded is not None and recorded != migration.checksum:
            raise ProjectMigrationError(
                f"{project_id}: migration {migration.version:04d} "
                f"({migration.name}) was edited after apply; project "
                f"migrations are immutable — write a new one instead")

    newly_applied: list[int] = []
    for migration in available:
        if migration.version in already:
            continue
        with database.transaction() as connection:
            connection.execute(migration.sql)
            connection.execute(
                "INSERT INTO sys.project_schema_migration "
                "(project_id, version, name, checksum, applied_at, "
                "application_version) VALUES (?, ?, ?, ?, ?, ?)",
                [project_id, migration.version, migration.name,
                 migration.checksum, datetime.now(timezone.utc),
                 application_version],
            )
        newly_applied.append(migration.version)
    return newly_applied
