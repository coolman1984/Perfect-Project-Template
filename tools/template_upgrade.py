#!/usr/bin/env python3
"""Upgrade a copied employee engine from one sealed master baseline to another.

The upgrade owns only core/tooling files named by the sealed baseline. Project-
owned files are never copied from the payload and never deleted by this tool.
Every apply creates a rollback snapshot before changing the local core.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from tools._common import EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, utc_now

BASELINE_NAME = "TEMPLATE_BASELINE.json"
ROLLBACK_ROOT = ".template_rollback"
UPGRADE_HISTORY = "UPGRADE_HISTORY.jsonl"
CORE_SCOPES = {"universal_core", "tooling"}


class UpgradeError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise UpgradeError(f"cannot read {path}: {error}") from error


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(value: str) -> Path:
    path = Path(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise UpgradeError(f"unsafe baseline path: {value!r}")
    return path


def _scope(relative: str, baseline: dict[str, Any]) -> str:
    value = relative.replace("\\", "/").lstrip("./")
    for rule in baseline.get("scope_rules", []):
        if fnmatch.fnmatchcase(value, str(rule.get("pattern", ""))):
            return str(rule.get("scope", "unknown"))
    return "unknown"


def verify_sealed_root(root: Path) -> dict[str, Any]:
    baseline_path = root / BASELINE_NAME
    baseline = _load_json(baseline_path)
    if not baseline.get("sealed"):
        raise UpgradeError(f"{baseline_path} is not a sealed master baseline")
    core_files = baseline.get("core_files", {})
    if not isinstance(core_files, dict) or not core_files:
        raise UpgradeError("sealed baseline has no core_files hashes")
    for relative, expected in sorted(core_files.items()):
        rel = _safe_relative(relative)
        if _scope(relative, baseline) not in CORE_SCOPES:
            raise UpgradeError(
                f"sealed core_files contains non-core path {relative!r}")
        path = root / rel
        if not path.is_file():
            raise UpgradeError(f"sealed core file missing: {relative}")
        actual = _sha256(path)
        if actual != expected:
            raise UpgradeError(
                f"sealed core hash mismatch: {relative}; "
                f"expected {expected}, found {actual}")
    return baseline


def _copy_atomic(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, delete=False,
        prefix=destination.name + ".", suffix=".upgrade.tmp") as handle:
        temporary = Path(handle.name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _backup_name(version: str) -> str:
    stamp = utc_now().replace(":", "").replace("-", "")
    safe_version = "".join(
        ch if ch.isalnum() or ch in "._-" else "_" for ch in version)
    return f"{stamp}_{safe_version}"


def _write_history(root: Path, payload: dict[str, Any]) -> None:
    path = root / UPGRADE_HISTORY
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def verify_project_packs(root: Path) -> list[str]:
    """Validate complete project packs after upgrade; discovery packs may wait."""
    projects_root = root / "projects"
    if not projects_root.exists():
        return []
    # Import through the target root so validation reflects the upgraded copy.
    from factory.project_contract import ProjectContractError, load_project
    verified: list[str] = []
    for directory in sorted(projects_root.iterdir()):
        project_file = directory / "project.toml"
        if not directory.is_dir() or not project_file.is_file():
            continue
        try:
            import tomllib
            document = tomllib.loads(project_file.read_text("utf-8"))
        except Exception as error:
            raise UpgradeError(f"invalid project.toml in {directory}: {error}") from error
        if str(document.get("mode", "discovery")) == "discovery":
            continue
        try:
            contract = load_project(directory)
        except ProjectContractError as error:
            raise UpgradeError(
                f"project compatibility validation failed for {directory.name}: "
                f"{error}") from error
        verified.append(contract.project_id)
    return verified


def apply_upgrade(
    current_root: str | Path,
    payload_root: str | Path,
    *,
    validate_projects: bool = True,
) -> Path:
    current = Path(current_root).resolve()
    payload = Path(payload_root).resolve()
    old = verify_sealed_root(current)
    new = verify_sealed_root(payload)
    if old.get("template_id") != new.get("template_id"):
        raise UpgradeError(
            "payload belongs to a different template_id; refusing cross-product upgrade")
    old_version = str(old.get("template_version", "unknown"))
    new_version = str(new.get("template_version", "unknown"))
    if old_version == new_version:
        raise UpgradeError("payload template version equals current version")

    old_files = set(old["core_files"])
    new_files = set(new["core_files"])
    backup = current / ROLLBACK_ROOT / _backup_name(old_version)
    backup.mkdir(parents=True, exist_ok=False)

    manifest = {
        "schema_version": 1,
        "template_id": old.get("template_id"),
        "from_version": old_version,
        "to_version": new_version,
        "created_at": utc_now(),
        "old_core_files": sorted(old_files),
        "new_core_files": sorted(new_files),
        "removed_by_upgrade": sorted(old_files - new_files),
        "project_roots_preserved": ["projects/"],
    }
    try:
        for relative in sorted(old_files):
            source = current / _safe_relative(relative)
            destination = backup / "core" / _safe_relative(relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        shutil.copy2(current / BASELINE_NAME, backup / BASELINE_NAME)
        (backup / "rollback_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # Remove only old core paths retired by the new master. Project paths
        # cannot appear here because verify_sealed_root rejects non-core scope.
        for relative in sorted(old_files - new_files):
            (current / _safe_relative(relative)).unlink(missing_ok=True)
        for relative in sorted(new_files):
            _copy_atomic(
                payload / _safe_relative(relative),
                current / _safe_relative(relative),
            )
        _copy_atomic(payload / BASELINE_NAME, current / BASELINE_NAME)

        # Verify the copied bytes against the NEW sealed baseline before any
        # project is declared compatible.
        verify_sealed_root(current)
        verified_projects = (
            verify_project_packs(current) if validate_projects else [])
        _write_history(current, {
            "event": "upgrade",
            "status": "PASS",
            "template_id": old.get("template_id"),
            "from_version": old_version,
            "to_version": new_version,
            "backup": str(backup.relative_to(current)),
            "verified_projects": verified_projects,
            "at": utc_now(),
        })
        return backup
    except Exception:
        # Never leave an employee copy half-upgraded. Restore the exact old core
        # before surfacing the original failure.
        rollback_upgrade(current, backup, record_history=False)
        raise


def rollback_upgrade(
    current_root: str | Path,
    backup_root: str | Path,
    *,
    record_history: bool = True,
) -> None:
    current = Path(current_root).resolve()
    backup = Path(backup_root).resolve()
    manifest = _load_json(backup / "rollback_manifest.json")
    old_files = set(manifest.get("old_core_files", []))
    new_files = set(manifest.get("new_core_files", []))
    for relative in sorted(new_files - old_files):
        (current / _safe_relative(relative)).unlink(missing_ok=True)
    for relative in sorted(old_files):
        stored = backup / "core" / _safe_relative(relative)
        if not stored.is_file():
            raise UpgradeError(
                f"rollback snapshot is incomplete: missing {relative}")
        _copy_atomic(stored, current / _safe_relative(relative))
    _copy_atomic(backup / BASELINE_NAME, current / BASELINE_NAME)
    verify_sealed_root(current)
    if record_history:
        _write_history(current, {
            "event": "rollback",
            "status": "PASS",
            "template_id": manifest.get("template_id"),
            "from_version": manifest.get("to_version"),
            "to_version": manifest.get("from_version"),
            "backup": str(backup),
            "at": utc_now(),
        })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="PROJECT_TOOL template-upgrade")
    sub = parser.add_subparsers(dest="command")
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("--payload", required=True)
    rollback_parser = sub.add_parser("rollback")
    rollback_parser.add_argument("--backup", required=True)
    args = parser.parse_args(argv)
    report = Report(f"template-upgrade {args.command or ''}".strip())
    try:
        if args.command == "apply":
            backup = apply_upgrade(REPO_ROOT, Path(args.payload))
            report.note(f"upgrade applied; rollback snapshot: {backup}")
            return report.emit()
        if args.command == "rollback":
            rollback_upgrade(REPO_ROOT, Path(args.backup))
            report.note("rollback restored the previous sealed Universal Core")
            return report.emit()
    except UpgradeError as error:
        report.fail(str(error))
        return report.emit()
    parser.print_help()
    return EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
