"""Raw chunk writer, lineage stamping and record identity (Parts 6, 7.7, 8.2).

Layer 3. Every staged row carries the lineage that lets any dashboard number be
traced back to its exact source row in about thirty seconds (rule 8).

Two hashes give insert / update / unchanged in one pass with no guessing:

    business_key_hash  "Is this the same business record?"
    row_content_hash   "Did any of its values change?"

Neither hash replaces the human-readable business-key columns — they are an
index, not the meaning (Part 25.2).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.data.database import Database
from app.excel.port import Chunk, LineageStamp

#: Columns stamped onto every staged row (Part 7.7).
LINEAGE_COLUMNS = (
    "_run_id", "_report_id", "_source_id", "_source_file", "_source_file_hash",
    "_source_sheet", "_source_row_number", "_extracted_at", "_schema_version",
)


def _canonical(value: Any) -> str:
    """Stable text for hashing.

    Determinism is the whole point: the same logical row must hash identically
    across runs, machines and Python versions, or idempotency silently breaks.
    """
    if value is None:
        return "\x00NULL"
    text = str(value).strip()
    return text


# NOTE ON HASHING — deliberately absent from this module.
#
# `business_key_hash` and `row_content_hash` are computed in the report's own
# `sql/clean.sql`, not here. Two reasons:
#
#   1. They depend on the approved business key, which is report-specific, so
#      they are a report variation point rather than Factory Core.
#   2. A Python copy alongside the SQL copy would be two definitions of "same
#      record" that can silently diverge. One concept, one source (Part 21).
#
# The determinism requirement still holds: identical logical rows must hash
# identically across runs and machines, or idempotency breaks.


@dataclass
class StagingResult:
    rows_staged: int
    chunks: int


class StagingWriter:
    """Writes chunks straight to raw staging, never holding a file in memory."""

    def __init__(self, database: Database, table: str, columns: list[str]) -> None:
        self.database = database
        self.table = table
        self.columns = columns

    def clear_run(self, run_id: str) -> None:
        """Staging is per-run scratch space; a retry starts from a clean slate."""
        self.database.execute(f"DELETE FROM {self.table} WHERE _run_id = ?", [run_id])

    def write_chunk(self, chunk: Chunk, lineage: LineageStamp) -> int:
        connection = self.database.connect()
        placeholders = ", ".join("?" for _ in (*self.columns, *LINEAGE_COLUMNS))
        column_list = ", ".join((*self.columns, *LINEAGE_COLUMNS))
        statement = f"INSERT INTO {self.table} ({column_list}) VALUES ({placeholders})"

        extracted_at = lineage.extracted_at or datetime.now(timezone.utc).isoformat()
        index_of = {name: position for position, name in enumerate(chunk.column_names)}

        rows: list[list[Any]] = []
        for offset, values in enumerate(chunk.values):
            source_row = chunk.first_row + offset
            business = [
                values[index_of[column]] if column in index_of else None
                for column in self.columns
            ]
            rows.append(business + [
                lineage.run_id, lineage.report_id, lineage.source_id,
                lineage.source_file, lineage.source_file_hash, lineage.source_sheet,
                source_row, extracted_at, lineage.schema_version,
            ])

        if rows:
            connection.executemany(statement, rows)
        return len(rows)

    def checkpoint(self, chunk: Chunk, lineage: LineageStamp, rows_staged: int) -> None:
        """Durable restart point, so a crash resumes instead of restarting."""
        payload = json.dumps(
            [list(map(_canonical, row)) for row in chunk.values], sort_keys=True)
        self.database.execute(
            "INSERT INTO sys.checkpoint (run_id, source_id, sheet_name, chunk_number, "
            "first_row, last_completed_row, rows_staged, chunk_hash, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [lineage.run_id, lineage.source_id, lineage.source_sheet,
             chunk.chunk_number, chunk.first_row, chunk.last_row, rows_staged,
             hashlib.sha256(payload.encode("utf-8")).hexdigest(),
             datetime.now(timezone.utc)],
        )

    def stage(self, port: Any, lineage: LineageStamp) -> StagingResult:
        """Consume the extraction port, writing each chunk immediately."""
        self.clear_run(lineage.run_id)
        total = chunks = 0
        for chunk in port.chunks():
            staged = self.write_chunk(chunk, lineage)
            self.checkpoint(chunk, lineage, staged)
            total += staged
            chunks += 1
        return StagingResult(rows_staged=total, chunks=chunks)
