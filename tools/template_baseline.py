#!/usr/bin/env python3
"""Seal and verify the Universal Engine without depending on Git.

Master-core mode may seal a release baseline. Employee adaptation mode only
verifies it. The checked-in manifest therefore survives ZIP/copy delivery where
no repository history or system Git exists.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools._common import EXIT_BLOCKED, EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, iter_source_files, read_text, sha256_file, utc_now
from tools.path_scope import BASELINE_PATH, classify_scope, load_baseline

CORE_SCOPES = {"universal_core", "tooling"}


def snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    baseline = load_baseline()
    for relative in iter_source_files():
        key = str(relative).replace("\\", "/")
        if key == "TEMPLATE_BASELINE.json":
            continue
        if classify_scope(key, baseline=baseline) in CORE_SCOPES:
            result[key] = sha256_file(REPO_ROOT / relative)
    return dict(sorted(result.items()))


def seal(*, template_version: str) -> int:
    data = load_baseline()
    data["template_version"] = template_version
    data["status"] = "sealed_master_template"
    data["sealed"] = True
    data["sealed_at"] = utc_now()
    data["core_files"] = snapshot()
    BASELINE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"template baseline sealed: {len(data['core_files'])} core/tooling files")
    return EXIT_PASS


def verify() -> int:
    report = Report("template baseline verify")
    data = load_baseline()
    if not data.get("sealed"):
        report.block("TEMPLATE_BASELINE.json is development_unsealed. Master-core release must seal it before any employee copy is considered approved.")
        return report.emit()
    expected = data.get("core_files", {})
    actual = snapshot()
    for path in sorted(set(expected) - set(actual)):
        report.fail(f"sealed core file missing: {path}")
    for path in sorted(set(actual) - set(expected)):
        report.fail(f"new core/tooling file is outside the sealed baseline: {path}")
    for path in sorted(set(expected) & set(actual)):
        if expected[path] != actual[path]:
            report.fail(f"sealed core file changed: {path}")
    if expected == actual:
        report.note(f"sealed baseline matches {len(actual)} core/tooling files without Git")
    return report.emit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="PROJECT_TOOL template-baseline")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("verify")
    p_seal = sub.add_parser("seal")
    p_seal.add_argument("--version", required=True)
    args = parser.parse_args(argv)
    if args.command == "verify":
        return verify()
    if args.command == "seal":
        return seal(template_version=args.version)
    parser.print_help()
    return EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
