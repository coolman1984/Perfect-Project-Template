"""Cross-platform one-writer report locks with stale-process recovery."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.errors import AppError

REPO_ROOT = Path(__file__).resolve().parent.parent
_SAFE = re.compile(r"^[A-Za-z0-9._-]{1,120}$")


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


@dataclass
class ReportLock:
    path: Path
    released: bool = False

    def release(self) -> None:
        if self.released:
            return
        try:
            current = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            current = {}
        if current.get("pid") == os.getpid():
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
        self.released = True

    def __enter__(self) -> "ReportLock":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.release()


def acquire_report_lock(report_id: str, *, root: Path | None = None) -> ReportLock:
    """Acquire one exclusive writer lock or raise the registered REPORT_LOCKED error."""
    if not _SAFE.fullmatch(report_id):
        raise ValueError("invalid report_id")
    base = Path(root) if root is not None else REPO_ROOT / "runs" / "locks"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{report_id}.lock"
    payload = json.dumps({
        "report_id": report_id,
        "pid": os.getpid(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }, separators=(",", ":"))

    for attempt in range(2):
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        except FileExistsError:
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                owner = int(existing.get("pid", -1))
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                owner = -1
            if not _pid_alive(owner) and attempt == 0:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
                continue
            raise AppError("REPORT_LOCKED", support_detail=f"report_id={report_id}; owner_pid={owner}")
        else:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            return ReportLock(path)
    raise AppError("REPORT_LOCKED", support_detail=f"report_id={report_id}")
