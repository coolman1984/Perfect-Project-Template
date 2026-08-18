#!/usr/bin/env python3
"""Report configuration scaffolding and validation (Constitution Parts 4, 5, 41).

The `PENDING_APPROVAL` sentinel is what turns "AI never invents business
meaning" from a paragraph into a check. An agent may freely *create* sentinels —
that is the correct way to record "a human must decide this". An agent may never
*resolve* one (Part 41.3).
"""

from __future__ import annotations

import argparse
import re
import shutil
import tomllib
from pathlib import Path

from tools._common import EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, read_text

REPORTS_ROOT = REPO_ROOT / "reports"
TEMPLATE_DIR = REPORTS_ROOT / "_TEMPLATE"
SENTINEL = "PENDING_APPROVAL"

REPORT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,48}$")


def _iter_reports() -> list[Path]:
    if not REPORTS_ROOT.exists():
        return []
    return sorted(
        path for path in REPORTS_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )


#: Comment markers per file type. A sentinel inside a commented-out example is
#: documentation showing the expected shape, not an open decision — counting it
#: inflates the number a human has to work through and trains them to ignore it.
COMMENT_MARKERS = {".toml": ("#",), ".sql": ("--", "#"), ".md": ()}


def _find_sentinels(text: str, suffix: str = "") -> list[tuple[int, str]]:
    markers = COMMENT_MARKERS.get(suffix, ())
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if SENTINEL not in line:
            continue
        stripped = line.strip()
        if markers and stripped.startswith(markers):
            continue
        hits.append((lineno, stripped))
    return hits


def cmd_new(report_id: str, title: str) -> int:
    report = Report(f"report new --id {report_id}")

    if not REPORT_ID_PATTERN.match(report_id):
        report.fail(f"invalid report id {report_id!r}: use lower_snake_case, 3-49 chars")
        return report.emit()
    if not TEMPLATE_DIR.exists():
        report.block(f"missing template at {TEMPLATE_DIR.relative_to(REPO_ROOT)}")
        return report.emit()

    destination = REPORTS_ROOT / report_id
    if destination.exists():
        report.fail(f"reports/{report_id}/ already exists — refusing to overwrite")
        return report.emit()

    shutil.copytree(TEMPLATE_DIR, destination)

    label = title or report_id.replace("_", " ").title()
    for path in sorted(destination.rglob("*")):
        if not path.is_file() or path.suffix not in {".toml", ".md", ".sql"}:
            continue
        text = read_text(path)
        text = text.replace("<REPORT_ID>", report_id).replace("<REPORT_TITLE>", label)
        path.write_text(text, encoding="utf-8")

    report.note(f"created reports/{report_id}/ from the template")
    report.note(f"title: {label}")
    report.note("")
    report.note("Every business decision is PENDING_APPROVAL. Part 3.1 reserves these")
    report.note("to a named human. Fill report_definition.md WITH the business owner")
    report.note("before writing any extraction code (Part 4 hard gate).")
    report.note(f"Then: PROJECT_TOOL report validate --id {report_id}")
    return report.emit()


def _lookup_config_value(config: dict, key: str) -> object:
    """Find an approvable value anywhere in the config.

    Approvable keys live in different sections — `business_key` in [history],
    `control_total_column` in [quality], `storage_allowed` in [output]. Hard-
    coding a subset silently skipped storage_allowed, which is exactly the
    IT-approved location that Part 13.5 requires a human to sign off.
    """
    if key in config and not isinstance(config[key], dict):
        return config[key]
    for section in config.values():
        if isinstance(section, dict) and key in section:
            return section[key]
    return None


def _validate_one(report_path: Path, mode: str, report: Report) -> None:
    report_id = report_path.name
    config_path = report_path / "report.toml"
    definition_path = report_path / "report_definition.md"

    if not config_path.exists():
        report.fail(f"{report_id}: missing report.toml (Part 5)")
        return
    if not definition_path.exists():
        report.fail(f"{report_id}: missing report_definition.md (Part 4 hard gate)")

    try:
        config = tomllib.loads(read_text(config_path))
    except tomllib.TOMLDecodeError as error:
        report.fail(f"{report_id}: report.toml is not valid TOML: {error}")
        return

    for key in ("report_id", "report_version", "load_mode", "timezone", "currency"):
        if key not in config:
            report.fail(f"{report_id}: report.toml missing top-level '{key}' (Part 5)")

    if config.get("report_id") not in (report_id, None):
        report.fail(f"{report_id}: report_id in TOML is "
                    f"{config.get('report_id')!r}, folder says {report_id!r}")

    load_mode = config.get("load_mode")
    if load_mode not in (None, SENTINEL, "append", "upsert", "snapshot", "replace_period"):
        report.fail(f"{report_id}: invalid load_mode {load_mode!r} (Part 8.1)")

    for section in ("excel", "extraction", "history", "quality", "output"):
        if section not in config:
            report.fail(f"{report_id}: report.toml missing [{section}] section (Part 5)")

    # Part 5: no path, sheet name, column name or threshold in a .py file.
    sentinels: list[tuple[Path, int, str]] = []
    for path in sorted(report_path.rglob("*")):
        if path.is_file() and path.suffix in {".toml", ".md", ".sql"}:
            for lineno, line in _find_sentinels(read_text(path), path.suffix):
                sentinels.append((path.relative_to(REPO_ROOT), lineno, line))

    approvals = config.get("approvals", {})
    for key, record in approvals.items() if isinstance(approvals, dict) else []:
        if not isinstance(record, dict):
            continue
        value = _lookup_config_value(config, key)
        approved_by = str(record.get("approved_by", "")).strip()
        if value and value != SENTINEL and not approved_by:
            report.fail(f"{report_id}: '{key}' has a value but no approver — "
                        f"both halves are required (Part 41.2)")
        if approved_by == "FIXTURE" and mode == "production":
            report.fail(f"{report_id}: '{key}' is approved by FIXTURE, which is "
                        f"invalid in production mode (Part 41.4)")

    if sentinels:
        if mode == "production":
            report.fail(f"{report_id}: {len(sentinels)} unresolved {SENTINEL} item(s) — "
                        f"forbidden in production mode (Part 41.3)")
            for path, lineno, line in sentinels[:15]:
                report.fail(f"    {path}:{lineno}  {line[:88]}")
        else:
            report.warn(f"{report_id}: {len(sentinels)} unresolved {SENTINEL} item(s) — "
                        f"allowed in {mode} mode, outputs must be watermarked "
                        f"UNAPPROVED DEFINITION (Part 41.3)")
            for path, lineno, line in sentinels[:15]:
                report.note(f"    {path}:{lineno}  {line[:88]}")
            if len(sentinels) > 15:
                report.note(f"    ... and {len(sentinels) - 15} more")
    else:
        report.note(f"{report_id}: no unresolved approvals")


def cmd_validate(report_id: str, mode: str) -> int:
    report = Report(f"report validate (mode={mode})")

    targets = _iter_reports()
    if report_id:
        targets = [path for path in targets if path.name == report_id]
        if not targets:
            report.fail(f"no such report: reports/{report_id}/")
            return report.emit()

    if not targets:
        report.note("no reports configured yet — expected before Phase 0 "
                    "(run 'PROJECT_TOOL report new --id <id>')")
        return report.emit()

    for path in targets:
        _validate_one(path, mode, report)

    report.note("")
    report.note("Part 41.3: an agent may create sentinels, never resolve them. "
                "Resolution needs a named human, a timestamp and evidence.")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command == "new":
        return cmd_new(args.report_id, args.title)
    if args.command == "validate":
        return cmd_validate(args.report_id, args.mode)
    print(f"usage error: unknown report command {args.command!r}")
    return EXIT_FAIL
