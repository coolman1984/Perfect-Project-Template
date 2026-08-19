"""Prepare and verify the exact Windows wheelhouse used by release builds."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from tools._common import REPO_ROOT

LOCKS = (
    REPO_ROOT / "requirements-lock.txt",
    REPO_ROOT / "requirements-build-lock.txt",
)


class WheelhouseError(RuntimeError):
    """The local dependency cache cannot support a reproducible build."""


def _require_windows_python() -> None:
    if os.name != "nt" or sys.version_info[:2] != (3, 12):
        raise WheelhouseError("wheelhouse preparation requires Windows x64 and Python 3.12")
    if sys.maxsize <= 2**32:
        raise WheelhouseError("wheelhouse preparation requires 64-bit Python")


def _base_requirement_args() -> list[str]:
    result: list[str] = []
    for lock in LOCKS:
        result.extend(("-r", str(lock)))
    return result


def verify(wheelhouse: Path) -> None:
    _require_windows_python()
    wheelhouse = wheelhouse.resolve()
    if not wheelhouse.is_dir() or not any(wheelhouse.glob("*.whl")):
        raise WheelhouseError(f"wheelhouse is missing or empty: {wheelhouse}")
    command = [
        sys.executable, "-m", "pip", "install", "--dry-run", "--ignore-installed",
        "--no-index", "--only-binary=:all:", "--find-links", str(wheelhouse),
        "--require-hashes", *_base_requirement_args(),
    ]
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def prepare(output_dir: Path) -> Path:
    _require_windows_python()
    output = output_dir.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work = REPO_ROOT / "work"
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wheelhouse-", dir=work) as temporary:
        candidate = Path(temporary) / "offline_packages"
        candidate.mkdir()
        command = [
            sys.executable, "-m", "pip", "download", "--only-binary=:all:",
            "--dest", str(candidate), "--require-hashes", *_base_requirement_args(),
        ]
        subprocess.run(command, cwd=REPO_ROOT, check=True)
        verify(candidate)
        backup: Path | None = None
        if output.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = work / f"offline_packages.backup.{stamp}"
            output.replace(backup)
        try:
            shutil.move(str(candidate), output)
        except OSError:
            if backup is not None and backup.exists() and not output.exists():
                backup.replace(output)
            raise
    return output


def main(args: argparse.Namespace) -> int:
    try:
        if args.command == "prepare":
            result = prepare(Path(args.output_dir))
            print(f"wheelhouse prepare: PASS — {result}")
            return 0
        if args.command == "verify":
            verify(Path(args.wheelhouse))
            print("wheelhouse verify: PASS")
            return 0
    except (OSError, subprocess.CalledProcessError, WheelhouseError) as error:
        print(f"wheelhouse {args.command}: FAIL — {error}")
        return 1
    print("wheelhouse: usage error")
    return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--output-dir", default="offline_packages")
    parser.add_argument("--wheelhouse", default="offline_packages")
    raise SystemExit(main(parser.parse_args()))
