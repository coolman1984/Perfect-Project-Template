#!/usr/bin/env python3
"""Acceptance gate ledger (Constitution Part 38).

Turns the prose gates of Parts 14, 28.1, 31.1 and 33 into a queryable file, so
"what is actually proven?" survives the end of an agent session.

Enforced here:
  - `pass` requires an evidence path that exists on disk (Part 38.2 rule 1)
  - `conditional` requires a reason and a next action  (rule 2)
  - `not_applicable` requires a reason                 (rule 3)
  - no release while a `block` gate is unproven        (rule 4)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools._common import EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, read_text, utc_now
from tools._miniyaml import MiniYamlError, dump_records, load_records

LEDGER_PATH = REPO_ROOT / "acceptance" / "gates.yaml"

VALID_STATUS = {"not_started", "in_progress", "pass", "fail", "conditional", "not_applicable"}
VALID_SEVERITY = {"block", "major", "minor"}

FIELD_ORDER = [
    "id", "part", "title", "severity", "status", "evidence",
    "verified_at", "verified_by", "conditional_reason", "next_action",
]

LEDGER_HEADER = """acceptance/gates.yaml — the machine-readable acceptance ledger (Constitution Part 38)

Edit through `PROJECT_TOOL gates set`, not by hand, so evidence is validated
at the moment a gate changes state.

  status: not_started | in_progress | pass | fail | conditional | not_applicable
  severity: block (no release without it) | major | minor

A gate moves to `pass` only in the same change set as the evidence it cites."""


def load_ledger() -> list[dict[str, str]]:
    if not LEDGER_PATH.exists():
        return []
    return load_records(read_text(LEDGER_PATH))


def save_ledger(records: list[dict[str, str]]) -> None:
    ordered = []
    for record in records:
        row = {key: record.get(key, "") for key in FIELD_ORDER}
        for key, value in record.items():
            if key not in row:
                row[key] = value
        ordered.append(row)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(dump_records(ordered, LEDGER_HEADER), encoding="utf-8")


def _validate(records: list[dict[str, str]], report: Report) -> None:
    seen: set[str] = set()
    for record in records:
        gate_id = record.get("id", "")
        if not gate_id:
            report.fail("a gate record has no id")
            continue
        if gate_id in seen:
            report.fail(f"duplicate gate id: {gate_id}")
        seen.add(gate_id)

        status = record.get("status", "")
        severity = record.get("severity", "")
        if status not in VALID_STATUS:
            report.fail(f"{gate_id}: invalid status {status!r}")
        if severity not in VALID_SEVERITY:
            report.fail(f"{gate_id}: invalid severity {severity!r}")

        if status == "pass":
            evidence = record.get("evidence", "").strip()
            if not evidence:
                report.fail(f"{gate_id}: status=pass with no evidence path (Part 38.2 rule 1)")
            elif not (REPO_ROOT / evidence).exists():
                report.fail(
                    f"{gate_id}: evidence path does not exist: {evidence} "
                    f"— a gate cannot pass on a sentence (Part 38.2 rule 1)")
            if not record.get("verified_at", "").strip():
                report.fail(f"{gate_id}: status=pass with no verified_at")

        if status == "conditional":
            if not record.get("conditional_reason", "").strip():
                report.fail(f"{gate_id}: conditional with no reason (Part 38.2 rule 2)")
            if not record.get("next_action", "").strip():
                report.fail(f"{gate_id}: conditional with no next_action (Part 38.2 rule 2)")

        if status == "not_applicable" and not record.get("conditional_reason", "").strip():
            report.fail(f"{gate_id}: not_applicable with no reason (Part 38.2 rule 3)")

        if status in {"not_started", "in_progress", "fail"} and \
                not record.get("next_action", "").strip():
            report.warn(f"{gate_id}: status={status} with no next_action")


def cmd_status(severity_filter: str | None, only: str | None) -> int:
    report = Report("gates status")
    if not LEDGER_PATH.exists():
        report.block(f"no ledger at {LEDGER_PATH.relative_to(REPO_ROOT)} "
                     f"— run Phase −2 instantiation (Part 39)")
        return report.emit()

    try:
        records = load_ledger()
    except MiniYamlError as error:
        report.fail(f"cannot parse the ledger: {error}")
        return report.emit()

    _validate(records, report)

    shown = [
        r for r in records
        if (not severity_filter or r.get("severity") == severity_filter)
        and (not only or r.get("status") == only)
    ]

    counts: dict[str, int] = {}
    for record in records:
        counts[record.get("status", "?")] = counts.get(record.get("status", "?"), 0) + 1

    print("=== gates status ===")
    print(f"  ledger: {LEDGER_PATH.relative_to(REPO_ROOT)}  ({len(records)} gates)")
    print("  " + "  ".join(f"{status}={count}" for status, count in sorted(counts.items())))

    print(f"\n  {'GATE':<38} {'SEV':<6} {'STATUS':<15} EVIDENCE")
    for record in shown:
        evidence = record.get("evidence", "") or record.get("next_action", "")[:44]
        print(f"  {record.get('id', '?'):<38} {record.get('severity', '?'):<6} "
              f"{record.get('status', '?'):<15} {evidence}")

    blockers = [r for r in records
                if r.get("severity") == "block"
                and r.get("status") not in {"pass", "not_applicable"}]
    print(f"\n  release blockers outstanding: {len(blockers)}")
    if blockers:
        print("  RELEASE IS BLOCKED (Part 38.2 rule 4). Outstanding:")
        for record in blockers[:12]:
            print(f"    - {record.get('id')}: {record.get('status')}")
        if len(blockers) > 12:
            print(f"    ... and {len(blockers) - 12} more")

    # Outstanding block gates are the normal state of a project in progress, so
    # they are reported, not failed. Only a malformed ledger fails the command.
    return report.emit()


def cmd_set(args: argparse.Namespace) -> int:
    report = Report(f"gates set {args.gate_id}")
    if not LEDGER_PATH.exists():
        report.block("no ledger to update")
        return report.emit()

    records = load_ledger()
    match = next((r for r in records if r.get("id") == args.gate_id), None)
    if match is None:
        report.fail(f"unknown gate id: {args.gate_id}")
        report.note("Add the gate to acceptance/gates.yaml first if it is genuinely new.")
        return report.emit()

    match["status"] = args.status
    if args.evidence:
        match["evidence"] = args.evidence
    if args.verified_by:
        match["verified_by"] = args.verified_by
    if args.conditional_reason:
        match["conditional_reason"] = args.conditional_reason
    if args.next_action:
        match["next_action"] = args.next_action
    match["verified_at"] = utc_now()

    _validate([match], report)
    if report.failures:
        report.note("Ledger NOT written — fix the problems above and retry.")
        return report.emit()

    save_ledger(records)
    report.note(f"{args.gate_id} -> {args.status}")
    report.note(f"wrote {LEDGER_PATH.relative_to(REPO_ROOT)}")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command == "status":
        return cmd_status(getattr(args, "severity", None), getattr(args, "only", None))
    if args.command == "set":
        return cmd_set(args)
    print(f"usage error: unknown gates command {args.command!r}")
    return EXIT_FAIL
