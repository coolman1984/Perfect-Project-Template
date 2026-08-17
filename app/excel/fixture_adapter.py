"""Fixture extraction adapter — DEV/TEST ONLY (Constitution Part 44.3).

This adapter exists so Phases 2-10 are testable on any machine, in CI, by any
agent. It is not a fallback and not a shortcut.

Four rules, all machine-checked:

1. **It never ships.** A release containing this file, or able to select this
   adapter, fails `architecture verify --release` (Part 44.3 rule 1).
2. **Its output is watermarked.** Every run through it sets `demo_data: true`
   in the dashboard JSON, the standalone HTML and the run manifest, and the UI
   labels it DEMO DATA (Parts 0.4 rule 7, 44.3 rule 2).
3. **It cannot prove the protected-file gate.** `GATE_PROTECTED_FILE_PROOF` is
   satisfiable only by the COM adapter against a real protected workbook, no
   matter how much fixture testing passes (Part 44.3 rule 3).
4. **It is never selected automatically.** Not on COM failure, not to keep a
   run green. COM failure fails closed per Parts 7.8 and 23.11. Automatic
   selection is the Part 27.8 "agent removes a dependency to make it portable"
   violation with a friendlier name (Part 44.3 rule 4).

Selection requires BOTH `adapter = "fixture"` in config AND the environment
variable `ADAPTER_FIXTURE_ACK=1`, so it can never be reached by accident.
"""

from __future__ import annotations

import csv
import hashlib
import os
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.excel.port import Chunk, ExtractionPort, LineageStamp, WorkbookIdentity, rows_per_chunk

ACK_VARIABLE = "ADAPTER_FIXTURE_ACK"


class FixtureAdapterNotAcknowledged(RuntimeError):
    """The fixture adapter was selected without the explicit acknowledgement."""


class FixtureExtractionAdapter(ExtractionPort):
    """Replays a CSV fixture as if it were an Excel sheet.

    CSV is used only as a convenient *fixture* carrier for dev and test. It is
    emphatically not an approved storage or history format — Part 0.7 forbids
    replacing the pipeline with a CSV/JSON folder.
    """

    #: Fixture data can never constitute production evidence (Part 44.3 rule 3).
    provides_production_evidence = False

    def __init__(self, fixture_path: str | Path) -> None:
        if os.environ.get(ACK_VARIABLE) != "1":
            raise FixtureAdapterNotAcknowledged(
                f"The fixture adapter is dev/test only. Set {ACK_VARIABLE}=1 to "
                f"acknowledge that its output is DEMO DATA and can never "
                f"satisfy GATE_PROTECTED_FILE_PROOF (Part 44.3).")
        self._fixture_path = Path(fixture_path)
        self._identity: WorkbookIdentity | None = None
        self._config: dict[str, Any] = {}
        self._header: list[str] = []
        self._rows: list[list[str]] = []
        self._run_id = "RUN-00000000-000"

    def open(self, source_path: str, config: dict[str, Any]) -> WorkbookIdentity:
        self._config = config
        self._run_id = str(config.get("run_id", self._run_id))

        with self._fixture_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        if not rows:
            raise ValueError(f"empty fixture: {self._fixture_path}")
        self._header, self._rows = rows[0], rows[1:]

        payload = self._fixture_path.read_bytes()
        stat = self._fixture_path.stat()
        self._identity = WorkbookIdentity(
            full_path=str(self._fixture_path.resolve()),
            sheet_name=str(config.get("sheet", "FIXTURE")),
            file_hash=hashlib.sha256(payload).hexdigest(),
            file_size=stat.st_size,
            modified_time=datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc).isoformat(),
            date_system_1904=False,
            open_mode="fixture",
        )
        return self._identity

    def chunks(self) -> Iterator[Chunk]:
        if self._identity is None:
            raise RuntimeError("open() must be called before chunks()")

        extraction = self._config.get("extraction", {})
        per_chunk = rows_per_chunk(
            target_cells=int(extraction.get("target_cells_per_chunk", 250_000)),
            column_count=max(1, len(self._header)),
            minimum=int(extraction.get("min_rows_per_chunk", 250)),
            maximum=int(extraction.get("max_rows_per_chunk", 10_000)),
        )

        for index, start in enumerate(range(0, len(self._rows), per_chunk), start=1):
            window = self._rows[start:start + per_chunk]
            yield Chunk(
                chunk_number=index,
                first_row=start + 2,          # 1-based, and row 1 is the header
                last_row=start + len(window) + 1,
                column_names=tuple(self._header),
                values=tuple(tuple(row) for row in window),
            )

    def lineage(self) -> LineageStamp:
        if self._identity is None:
            raise RuntimeError("open() must be called before lineage()")
        return LineageStamp(
            run_id=self._run_id,
            report_id=str(self._config.get("report_id", "fixture_report")),
            source_id="FIXTURE",
            source_file=self._identity.full_path,
            source_file_hash=self._identity.file_hash,
            source_sheet=self._identity.sheet_name,
            extracted_at=datetime.now(timezone.utc).isoformat(),
            schema_version=str(self._config.get("schema_version", "0")),
            extra={"demo_data": "true"},
        )

    def close(self) -> None:
        self._rows = []
        self._header = []
