"""Parquet recovery archive (Constitution Parts 6 layer 7, 13.3).

Purpose: recovery, rebuild, fast historical analysis, compressed storage.

The archive is what makes "database lost" a minutes-long problem instead of a
re-extraction of every source file — the only genuinely slow path (Part 8.6).

Partitioned by report/year/month. Avoid thousands of tiny files (Part 13.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.data.database import Database


@dataclass(frozen=True)
class ArchiveResult:
    path: Path
    rows: int


def archive_history(
    database: Database,
    *,
    history_table: str,
    report_id: str,
    archive_root: Path,
    event_date_column: str,
) -> ArchiveResult:
    """Write active trusted history to a partitioned Parquet dataset."""
    destination = Path(archive_root) / f"report={report_id}"
    destination.mkdir(parents=True, exist_ok=True)

    rows = int(database.scalar(
        f"SELECT count(*) FROM {history_table} WHERE is_active = TRUE") or 0)

    # DuckDB writes the Parquet partitions directly; no extension download is
    # involved, which keeps the run offline (Part 23.6).
    database.execute(f"""
        COPY (
            SELECT *,
                   CAST(strftime({event_date_column}, '%Y') AS INTEGER) AS year,
                   CAST(strftime({event_date_column}, '%m') AS INTEGER) AS month
            FROM {history_table}
            WHERE is_active = TRUE
        ) TO '{destination.as_posix()}'
        (FORMAT PARQUET, PARTITION_BY (year, month), OVERWRITE_OR_IGNORE)
    """)
    return ArchiveResult(path=destination, rows=rows)


def rebuild_history_from_archive(
    database: Database, *, history_table: str, archive_root: Path, report_id: str
) -> int:
    """Restore trusted history from the archive alone.

    This is the proof behind GATE_ARCHIVE_REBUILD: a fresh database must be
    reconstructable without touching Excel.
    """
    source = Path(archive_root) / f"report={report_id}"
    if not source.exists():
        raise FileNotFoundError(f"no archive to rebuild from: {source}")

    columns = database.columns_of(history_table)
    column_list = ", ".join(columns)
    database.execute(f"DELETE FROM {history_table}")
    database.execute(f"""
        INSERT INTO {history_table} ({column_list})
        SELECT {column_list} FROM read_parquet('{source.as_posix()}/**/*.parquet')
    """)
    return int(database.scalar(f"SELECT count(*) FROM {history_table}") or 0)
