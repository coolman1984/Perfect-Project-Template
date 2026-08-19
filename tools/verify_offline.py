"""Verify the built release without installing or downloading anything."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from tools._common import REPO_ROOT


def executable_json(executable: Path, argument: str) -> dict[str, object]:
    completed = subprocess.run(
        [str(executable), argument], capture_output=True, text=True, timeout=60)
    if completed.returncode:
        raise RuntimeError(
            f"{argument} failed ({completed.returncode}): "
            f"{completed.stdout}\n{completed.stderr}")
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def verify(release: Path) -> None:
    executable = release / "app" / "excel-intelligence.exe"
    if not executable.is_file():
        raise RuntimeError(f"missing release executable: {executable}")
    integrity = executable_json(executable, "--verify-package")
    runtime = executable_json(executable, "--self-test")
    if integrity.get("status") != "PASS" or runtime.get("status") != "PASS":
        raise RuntimeError("release runtime or integrity self-test did not pass")
    leakage = []
    for path in (release / "app").rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(release).as_posix()
        if path.suffix.lower() == ".spec" or any(
            marker in relative
            for marker in ("/_internal/app/", "/_internal/tools/", "/tests/")
        ):
            leakage.append(relative)
    if leakage:
        raise RuntimeError(f"developer source leaked into runtime app: {leakage}")

    evidence_root = REPO_ROOT / "release"
    common = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "release": str(release.resolve()),
        "network_downloads": 0,
        "developer_source_leakage": leakage,
    }
    (evidence_root / "ARCHITECTURE_EVIDENCE.json").write_text(
        json.dumps({**common, "status": "PASS", "integrity": integrity}, indent=2)
        + "\n", encoding="utf-8")
    (evidence_root / "LOCAL_TRANSPORT_EVIDENCE.json").write_text(
        json.dumps({**common, "status": "PASS", "runtime": runtime}, indent=2)
        + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "integrity": integrity, "runtime": runtime}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "release", nargs="?", default=str(REPO_ROOT / "release" / "current"))
    args = parser.parse_args()
    verify(Path(args.release))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
