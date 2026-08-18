"""Reusable run orchestration. Owns order and publication, never business formulas."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app import events
from app.data.database import Database
from app.excel.com_adapter import ComExtractionAdapter
from app.excel.fixture_adapter import FixtureExtractionAdapter
from app.locks import acquire_report_lock
from app.pipeline import Pipeline, ReportContract, RunOutcome

REPO_ROOT = Path(__file__).resolve().parent.parent


def new_run_id() -> str:
    """Create an opaque sortable-enough id before a background run starts."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"RUN-{stamp}-{uuid.uuid4().hex[:8]}"


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run(
    report_id: str, sources: object, *, run_id: str | None = None,
    repo_root: Path | None = None, database_path: Path | None = None,
    requested_period: str | None = None,
) -> RunOutcome:
    """Run one configured report and publish only a successful new dashboard.

    One source is deliberately enforced in this vertical slice. Multiple
    unrelated workbooks require a source-composition contract that maps each
    role/table separately; concatenating them would manufacture false data.
    """
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    source_list = [sources] if isinstance(sources, (str, Path)) else list(sources)  # type: ignore[arg-type]
    if len(source_list) != 1:
        raise ValueError("this vertical slice accepts one source; multi-source reports must use an approved source-composition contract")
    source_path = Path(source_list[0]).resolve()
    rid = run_id or new_run_id()
    contract = ReportContract(root / "reports" / report_id)
    database = Database(database_path or root / "data" / "warehouse.duckdb")
    adapter: Any = FixtureExtractionAdapter(source_path) if contract.uses_fixture_adapter else ComExtractionAdapter()

    with acquire_report_lock(report_id, root=root / "runs" / "locks"):
        events.emit(rid, "STARTING", root=root / "runs", report_id=report_id)
        try:
            pipeline = Pipeline(database, contract)
            pipeline.prepare()
            identity = adapter.open(str(source_path), {
                "report_id": report_id, "run_id": rid,
                "sheet": contract.report.get("excel", {}).get("sheet", ""),
                "extraction": contract.report.get("extraction", {}),
            })
            events.emit(rid, "SOURCE_OPENED", root=root / "runs", source_file=identity.full_path)
            outcome = pipeline.run(rid, adapter, requested_period=requested_period)
            events.emit(rid, outcome.status, root=root / "runs", quality=outcome.quality_status)
            if outcome.succeeded and outcome.dashboard is not None:
                report_output = root / "output" / report_id / "dashboard.json"
                _atomic_json(report_output, outcome.dashboard)
                _atomic_json(root / "output" / "latest_dashboard.json", outcome.dashboard)
            return outcome
        except Exception as error:
            events.emit(rid, "FAILED", root=root / "runs", error_type=type(error).__name__)
            raise
        finally:
            try:
                adapter.close()
            finally:
                database.close()
