"""Quarantine: nothing is ever silently dropped (Constitution Part 9.5).

A rejected row is retained with its run, source row number, reason code, reason
message and raw values. "We dropped some bad rows" is not an acceptable answer
to a manager asking why a total moved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.data.database import Database

# Reason codes. Report-specific rules add their own; these are the Factory Core
# reasons every report can produce.
NEGATIVE_MEASURE = "NEGATIVE_MEASURE"
BLANK_BUSINESS_KEY = "BLANK_BUSINESS_KEY"
UNPARSEABLE_NUMBER = "UNPARSEABLE_NUMBER"
UNPARSEABLE_DATE = "UNPARSEABLE_DATE"
UNPARSEABLE_VALUE = "UNPARSEABLE_VALUE"
CONFLICTING_DUPLICATE = "CONFLICTING_DUPLICATE"
EXACT_DUPLICATE = "EXACT_DUPLICATE"

REASON_MESSAGES = {
    NEGATIVE_MEASURE: "A quantity was negative, which this report does not allow.",
    BLANK_BUSINESS_KEY: "The columns that identify this record were not all filled in.",
    UNPARSEABLE_NUMBER: "A value that should be a number could not be read as one.",
    UNPARSEABLE_DATE: "A value that should be a date could not be read as one.",
    UNPARSEABLE_VALUE: "A value did not match the type this column is configured to hold.",
    CONFLICTING_DUPLICATE: "The same record appears twice with different values.",
    EXACT_DUPLICATE: "An identical copy of this record appeared in the same file.",
}


@dataclass(frozen=True)
class QuarantinedRow:
    source_row: int | None
    reason_code: str
    raw_values: dict[str, Any]
    business_key_hash: str | None = None
    source_id: str | None = None
    source_sheet: str | None = None


def quarantine_rows(
    database: Database, run_id: str, report_id: str, rows: list[QuarantinedRow]
) -> int:
    """Store rejected rows. Returns how many were retained."""
    if not rows:
        return 0
    payload = [
        [run_id, report_id, row.source_id, row.source_sheet, row.source_row,
         row.business_key_hash, row.reason_code,
         REASON_MESSAGES.get(row.reason_code, row.reason_code),
         json.dumps(row.raw_values, sort_keys=True, default=str), "OPEN"]
        for row in rows
    ]
    database.connect().executemany(
        "INSERT INTO quality.quarantine (run_id, report_id, source_id, source_sheet, "
        "source_row, business_key_hash, reason_code, reason_message, raw_values, "
        "resolution_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", payload)
    return len(rows)


def count_for_run(database: Database, run_id: str) -> int:
    return int(database.scalar(
        "SELECT count(*) FROM quality.quarantine WHERE run_id = ?", [run_id]) or 0)


def summary_by_reason(database: Database, run_id: str) -> dict[str, int]:
    return {
        row[0]: int(row[1])
        for row in database.query(
            "SELECT reason_code, count(*) FROM quality.quarantine "
            "WHERE run_id = ? GROUP BY reason_code ORDER BY reason_code", [run_id])
    }
