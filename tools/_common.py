"""Shared helpers for the portable tool tier (Constitution Part 37). Stdlib only."""

from __future__ import annotations

import fnmatch
import hashlib
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

EXIT_PASS, EXIT_FAIL, EXIT_USAGE, EXIT_BLOCKED = 0, 1, 2, 3

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_ROOTS = {
    "runtime", "offline_packages", "repair_payload", "release", "dist", "build",
    "inbox", "workspace", "work", "data", "archive", "output", "runs", "logs",
    "licenses",
}
EXCLUDED_PREFIXES = ("web/vendor",)
EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules", ".ai_cache", ".ruff_cache",
}
EXCLUDED_GLOBS = (
    "*.pyc", "*.duckdb", "*.duckdb.wal", "*.parquet", "*.xlsx", "*.xlsm",
    "*.xlsb", "*.xls", "*.zip", "*.log", "*.jsonl.gz", "*.sqlite",
)
SOURCE_SUFFIXES = {
    ".py", ".sql", ".toml", ".json", ".md", ".html", ".css", ".js",
    ".yaml", ".yml", ".bat", ".sh", ".cfg", ".ini",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


GENERATED_FILES = {".ai/CONTEXT_PACK.md"}


def is_excluded(path: Path) -> bool:
    """True when a repo-relative path is outside the scanned source of truth."""
    key = str(path).replace("\\", "/")
    parts = path.parts
    if key in GENERATED_FILES:
        return True
    if set(parts) & EXCLUDED_DIRS:
        return True
    if parts and parts[0] in EXCLUDED_ROOTS:
        return True
    if any(key == prefix or key.startswith(f"{prefix}/") for prefix in EXCLUDED_PREFIXES):
        return True
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in EXCLUDED_GLOBS)


def iter_source_files(root: Path | None = None) -> list[Path]:
    """Every source-of-truth file, repo-relative, deterministically ordered."""
    root = root or REPO_ROOT
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath).relative_to(root)
        dirnames[:] = sorted(
            name for name in dirnames
            if not is_excluded(current / name if str(current) != "." else Path(name))
        )
        for filename in sorted(filenames):
            absolute = Path(dirpath) / filename
            relative = absolute.relative_to(root)
            if is_excluded(relative):
                continue
            if absolute.suffix in SOURCE_SUFFIXES or not absolute.suffix:
                if absolute.is_file():
                    found.append(relative)
    return sorted(found)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(131072), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def git_available(root: Path | None = None) -> bool:
    root = root or REPO_ROOT
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root, capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def git_changed_files(base: str, root: Path | None = None) -> list[str]:
    root = root or REPO_ROOT
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.SubprocessError):
        return []


def git_tracked_files(root: Path | None = None) -> set[str]:
    """Repo-relative paths git currently tracks. Empty set when git is absent."""
    root = root or REPO_ROOT
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, capture_output=True,
            text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    if result.returncode != 0:
        return set()
    return {item for item in result.stdout.split("\0") if item}


def git_ignored(paths: list[str], root: Path | None = None) -> set[str]:
    """Return ignored repo paths without Windows newline/quoting corruption.

    Git's normal newline protocol can preserve carriage returns as part of a
    path when `--stdin` crosses Windows text-mode boundaries. `-z` makes both
    input and output NUL-delimited, so spaces, Unicode, quotes and CRLF cannot
    mutate the filename being checked.
    """
    root = root or REPO_ROOT
    if not paths:
        return set()
    try:
        payload = "\0".join(paths) + "\0"
        result = subprocess.run(
            ["git", "check-ignore", "-z", "--stdin"],
            cwd=root, input=payload, capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    if result.returncode not in (0, 1):
        return set()
    return {item for item in result.stdout.split("\0") if item}


@dataclass
class Report:
    """Collect findings so a command reports every problem, not just the first."""

    title: str
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)

    def block(self, message: str) -> None:
        self.blocked.append(message)

    def emit(self) -> int:
        print(f"\n=== {self.title} ===")
        for note in self.notes:
            print(f"  .  {note}")
        for warning in self.warnings:
            print(f"  ~  WARNING  {warning}")
        for failure in self.failures:
            print(f"  X  FAIL     {failure}")
        for blocker in self.blocked:
            print(f"  ?  BLOCKED  {blocker}")

        if self.failures:
            print(f"\n{self.title}: FAIL ({len(self.failures)} failure(s), "
                  f"{len(self.warnings)} warning(s))")
            return EXIT_FAIL
        if self.blocked:
            print(f"\n{self.title}: BLOCKED — nothing was verified. "
                  f"Do not report this as a pass (Part 37.4).")
            return EXIT_BLOCKED
        print(f"\n{self.title}: PASS ({len(self.warnings)} warning(s))")
        return EXIT_PASS


def not_implemented(command: str, implement_in: str) -> int:
    """Part 37.3: an unimplemented command fails loudly and names its file."""
    print(f"TOOL_COMMAND_NOT_IMPLEMENTED: '{command}'")
    print(f"  Implement it in: {implement_in}")
    print("  This exits non-zero on purpose. A green check that proves nothing")
    print("  is worse than a missing check (Part 37.3).")
    return EXIT_FAIL
