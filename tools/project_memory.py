#!/usr/bin/env python3
"""Project memory and improvement scout (Constitution Parts 21.6, 21.7).

Memory is durable engineering evidence, not a chat transcript. Every record
needs a source and a date; business meaning needs a named approval owner.
`validate` fails on malformed, source-free, conflicting-active, or orphaned
records (Part 21.6 rule 6).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tools._common import EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, read_text

MEMORY_PATH = REPO_ROOT / ".ai" / "MEMORY.jsonl"
OPPORTUNITIES_PATH = REPO_ROOT / ".ai" / "OPPORTUNITIES.md"

VALID_TYPES = {"decision", "lesson", "constraint", "benchmark", "incident", "preference"}
VALID_STATUS = {"candidate", "validated", "superseded", "rejected"}
VALID_CONFIDENCE = {"verified", "approved", "inferred"}

REQUIRED_FIELDS = (
    "id", "type", "statement", "status", "source",
    "recorded_at", "owner", "confidence", "affected_paths",
)

# Patterns that suggest a raw sensitive value slipped into memory (rule 3).
SECRET_HINTS = re.compile(
    r"(password|passwd|secret|api[_-]?key|token|connection\s*string|pwd\s*=)",
    re.IGNORECASE,
)


def load_records() -> tuple[list[dict], list[str]]:
    """Return (records, parse_errors)."""
    if not MEMORY_PATH.exists():
        return [], []
    records, errors = [], []
    for lineno, line in enumerate(read_text(MEMORY_PATH).splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        try:
            records.append(json.loads(stripped))
        except json.JSONDecodeError as error:
            errors.append(f"line {lineno}: invalid JSON ({error.msg})")
    return records, errors


def cmd_validate() -> int:
    report = Report("memory validate")
    if not MEMORY_PATH.exists():
        report.fail(f"missing {MEMORY_PATH.relative_to(REPO_ROOT)} (Part 21.6)")
        return report.emit()

    records, errors = load_records()
    for error in errors:
        report.fail(f"MEMORY.jsonl {error}")

    seen: set[str] = set()
    superseded: set[str] = set()

    for index, record in enumerate(records, start=1):
        label = record.get("id") or f"record #{index}"

        for field in REQUIRED_FIELDS:
            if field not in record:
                report.fail(f"{label}: missing required field '{field}'")

        record_id = record.get("id", "")
        if record_id:
            if record_id in seen:
                report.fail(f"{label}: duplicate id")
            seen.add(record_id)
            if not record_id.startswith("MEM-"):
                report.fail(f"{label}: id must start with 'MEM-'")

        if record.get("type") not in VALID_TYPES:
            report.fail(f"{label}: invalid type {record.get('type')!r}")
        if record.get("status") not in VALID_STATUS:
            report.fail(f"{label}: invalid status {record.get('status')!r}")
        if record.get("confidence") not in VALID_CONFIDENCE:
            report.fail(f"{label}: invalid confidence {record.get('confidence')!r}")

        if not str(record.get("source", "")).strip():
            report.fail(f"{label}: empty source — memory needs evidence (Part 21.6 rule 2)")
        if not str(record.get("recorded_at", "")).strip():
            report.fail(f"{label}: empty recorded_at")

        statement = str(record.get("statement", ""))
        if not statement.strip():
            report.fail(f"{label}: empty statement")
        if SECRET_HINTS.search(statement):
            report.fail(f"{label}: statement looks like it contains a secret "
                        f"(Part 21.6 rule 3)")

        # Business meaning requires a named human, never an agent (Part 21.6 rule 2).
        if record.get("confidence") == "approved" and not str(record.get("owner", "")).strip():
            report.fail(f"{label}: confidence=approved with no named owner")

        paths = record.get("affected_paths", [])
        if not isinstance(paths, list):
            report.fail(f"{label}: affected_paths must be a list")
        else:
            for path in paths:
                if "*" in str(path) or str(path).endswith("/"):
                    continue
                if not (REPO_ROOT / str(path)).exists():
                    report.fail(f"{label}: orphaned affected_path {path!r} "
                                f"(Part 21.6 rule 6)")

        target = record.get("supersedes")
        if target:
            superseded.add(str(target))

    for target in superseded:
        if target not in seen:
            report.warn(f"a record supersedes unknown id {target!r}")

    active_by_statement: dict[str, str] = {}
    for record in records:
        if record.get("status") != "validated":
            continue
        key = str(record.get("statement", ""))[:80].lower()
        if key in active_by_statement:
            report.fail(
                f"two active records make the same claim: "
                f"{active_by_statement[key]} and {record.get('id')} "
                f"— supersede one instead of duplicating (Part 21.6 rule 4)")
        active_by_statement[key] = str(record.get("id"))

    report.note(f"{len(records)} memory record(s), {len(seen)} unique id(s)")
    if not records:
        report.note("empty memory is valid for a new project — records are added as "
                    "evidence appears, never invented up front")
    return report.emit()


def cmd_suggest(task: str, max_items: int) -> int:
    """Evidence-based improvement scout (Part 21.7).

    Deliberately conservative: it reports observable project facts and never
    invents business-shaped suggestions. Zero suggestions is a valid result.
    """
    report = Report("memory suggest")
    report.note(f"completed task: {task}")
    report.note(f"maximum suggestions: {max_items}")

    existing = read_text(OPPORTUNITIES_PATH) if OPPORTUNITIES_PATH.exists() else ""
    suggestions: list[tuple[str, str, str]] = []

    def propose(opportunity_id: str, evidence: str, proposal: str) -> None:
        if opportunity_id in existing:
            return  # deduplicate against the register (Part 21.7)
        if len(suggestions) < max_items:
            suggestions.append((opportunity_id, evidence, proposal))

    from tools import gates as gates_module

    if gates_module.LEDGER_PATH.exists():
        try:
            ledger = gates_module.load_ledger()
        except Exception:  # noqa: BLE001 - a broken ledger is reported by `gates status`
            ledger = []
        blockers = [r for r in ledger
                    if r.get("severity") == "block"
                    and r.get("status") not in {"pass", "not_applicable"}]
        if blockers:
            propose(
                "OPP-GATES-BLOCKERS",
                f"{len(blockers)} block-severity gate(s) are not yet proven; "
                f"next unproven: {blockers[0].get('id')}",
                "Close the highest-value blocking gate before optional scope "
                "(Part 21.7: correctness and data trust rank above features).",
            )
        conditional = [r for r in ledger if r.get("status") == "conditional"]
        if conditional:
            propose(
                "OPP-GATES-CONDITIONAL",
                f"{len(conditional)} gate(s) are CONDITIONAL pending a real environment",
                "Schedule the named next_action for each conditional gate so "
                "production approval is not silently deferred (Part 31.4).",
            )

    records, _ = load_records()
    if not records:
        propose(
            "OPP-MEMORY-EMPTY",
            "no memory records exist yet",
            "Record the first validated constraint or benchmark once real evidence "
            "exists. Do not backfill invented history (Part 21.6 rule 1).",
        )

    print("=== memory suggest ===")
    if not suggestions:
        print("  no evidence-based suggestions. Zero is a valid result (Part 21.7).")
    for opportunity_id, evidence, proposal in suggestions:
        print(f"\n  [{opportunity_id}]")
        print(f"    evidence: {evidence}")
        print(f"    proposal: {proposal}")
        print("    timing:   next")
        print("    note:     needs user approval before implementation (Part 21.7)")

    print("\n  Record accepted/deferred/rejected states in .ai/OPPORTUNITIES.md.")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command == "validate":
        return cmd_validate()
    if args.command == "suggest":
        return cmd_suggest(args.task, args.max_items)
    print(f"usage error: unknown memory command {args.command!r}")
    return EXIT_FAIL
