"""Employee project orchestration for the V8.1 adaptation-first runtime.

The shared application owns runtime, extraction adapters, database, events and
publication once. Project packs supply source roles, relationships, trusted SQL
and presentation configuration. A normal department never gets its own server.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tomllib
from typing import Any

from app import events
from app.data.database import Database
from app.errors import AppError
from app.excel.com_adapter import ComExtractionAdapter
from app.excel.fixture_adapter import FixtureExtractionAdapter
from app.locks import acquire_report_lock
from app.orchestrator import new_run_id
from app.project_pipeline import ProjectOutcome, ProjectPipeline
from factory.project_contract import find_project_directory, load_project

REPO_ROOT = Path(__file__).resolve().parent.parent


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _fixture_allowed(project_directory: Path) -> bool:
    document = tomllib.loads(
        (project_directory / "project.toml").read_text("utf-8"))
    execution = document.get("execution", {})
    return bool(execution.get("fixture_adapter", False))


def _adapter_for(
    project_directory: Path, source_path: Path
) -> Any:
    if source_path.suffix.lower() == ".csv":
        if not _fixture_allowed(project_directory):
            raise AppError(
                "SRC_NOT_FOUND",
                support_detail=(
                    "CSV fixture input is disabled for this employee project; "
                    "production Excel sources must use the authorized COM adapter"),
            )
        return FixtureExtractionAdapter(source_path)
    return ComExtractionAdapter()


def run_project(
    project_id: str,
    source_paths: dict[str, str | Path],
    *,
    run_id: str | None = None,
    repo_root: Path | None = None,
    database_path: Path | None = None,
    requested_periods: dict[str, str] | None = None,
) -> ProjectOutcome:
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    project_directory = find_project_directory(root / "projects", project_id)
    contract = load_project(project_directory)
    rid = run_id or new_run_id()

    unknown = sorted(set(source_paths) - contract.source_ids)
    if unknown:
        raise AppError(
            "SRC_NOT_FOUND",
            support_detail=f"unknown source role(s) for {project_id}: {unknown}",
        )
    missing = sorted(
        source.source_id for source in contract.sources
        if source.required and source.source_id not in source_paths)
    if missing:
        raise AppError(
            "SRC_NOT_FOUND",
            support_detail=f"required source role(s) not supplied: {missing}",
        )

    database = Database(database_path or root / "data" / "warehouse.duckdb")
    adapters: dict[str, Any] = {}
    with acquire_report_lock(project_id, root=root / "runs" / "locks"):
        events.emit(
            rid, "STARTING", root=root / "runs",
            project_id=project_id, source_count=len(source_paths))
        try:
            pipeline = ProjectPipeline(database, contract)
            pipeline.prepare()
            for source in contract.sources:
                if source.source_id not in source_paths:
                    continue
                path = Path(source_paths[source.source_id]).resolve()
                adapter = _adapter_for(project_directory, path)
                adapters[source.source_id] = adapter
                identity = adapter.open(str(path), {
                    "project_id": project_id,
                    # Compatibility field used by the extraction-port lineage
                    # contract until all old report wording is migrated.
                    "report_id": project_id,
                    "run_id": rid,
                    "source_id": source.source_id,
                    "sheet": source.sheet,
                    "extraction": {
                        "target_cells_per_chunk": 200_000,
                        "min_rows_per_chunk": 250,
                        "max_rows_per_chunk": 25_000,
                    },
                })
                events.emit(
                    rid, "SOURCE_OPENED", root=root / "runs",
                    project_id=project_id,
                    source_id=source.source_id,
                    source_file=identity.full_path,
                )

            events.emit(
                rid, "VALIDATING_PROJECT", root=root / "runs",
                project_id=project_id)
            outcome = pipeline.run(
                rid, adapters, requested_periods=requested_periods)
            events.emit(
                rid, outcome.status, root=root / "runs",
                project_id=project_id,
                quality=outcome.quality_status,
            )
            if outcome.succeeded and outcome.dashboard is not None:
                project_output = root / "output" / "projects" / project_id
                _atomic_json(project_output / "dashboard.json", outcome.dashboard)
                _atomic_json(
                    root / "output" / "latest_dashboard.json",
                    outcome.dashboard,
                )
            return outcome
        except Exception as error:
            events.emit(
                rid, "FAILED", root=root / "runs",
                project_id=project_id, error_type=type(error).__name__)
            raise
        finally:
            for adapter in adapters.values():
                try:
                    adapter.close()
                except Exception:
                    # The original processing error remains authoritative.
                    # Adapter cleanup failures are support evidence, not a
                    # reason to hide the processing error with a second one.
                    pass
            database.close()
