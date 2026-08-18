"""Durable ordered progress events for the local web application."""
from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
_ID = re.compile(r"^[A-Za-z0-9._-]{1,120}$")
_WRITE_LOCK = threading.Lock()


def _safe_id(value: str, label: str) -> str:
    if not _ID.fullmatch(value):
        raise ValueError(f"invalid {label}: use letters, numbers, dot, dash or underscore")
    return value


def _event_path(run_id: str, root: Path | None = None) -> Path:
    safe = _safe_id(run_id, "run_id")
    base = Path(root) if root is not None else REPO_ROOT / "runs"
    return base / safe / "events.jsonl"


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("sequence"), int):
            events.append(value)
    return events


def emit(run_id: str, stage: str, *, root: Path | None = None, **fields: object) -> dict[str, Any]:
    """Persist an event before returning it to any delivery layer."""
    _safe_id(run_id, "run_id")
    if not stage or len(stage) > 120:
        raise ValueError("stage is required and must be at most 120 characters")
    path = _event_path(run_id, root)
    with _WRITE_LOCK:
        prior = _read(path)
        sequence = prior[-1]["sequence"] + 1 if prior else 0
        event: dict[str, Any] = {
            "run_id": run_id,
            "sequence": sequence,
            "stage": stage,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        event.update(fields)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event


def since(run_id: str, sequence: int, *, root: Path | None = None) -> list[dict[str, Any]]:
    """Replay durable events strictly after `sequence`, in stored order."""
    return [event for event in _read(_event_path(run_id, root)) if event["sequence"] > sequence]
