#!/usr/bin/env python3
"""`PROJECT_TOOL factory` — the Excel Automation Project Factory.

Flow an employee follows (through the app UI, or here for an agent):

    new        name the automation and start the interview
    interview  answer plain-language business questions
    review     see what the system understood, in plain language
    approve    a HUMAN records an approval with provenance
    generate   write the technical contract from the answers
    brief      hand the coding agent a controlled work package
    status     what is confirmed, what needs approval, what is unknown
    validate   is this project in a state a coding agent should build from?
    reference  verify the Golden Reference still produces its known answers
"""

from __future__ import annotations

import argparse
import json
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from factory import approvals, build_brief, health
from factory.generator import GeneratorError, generate
from factory.questionnaire import CORE_QUESTIONS, Interview
from tools._common import EXIT_FAIL, EXIT_PASS, EXIT_USAGE, REPO_ROOT, Report, read_text

INTERVIEW_DIR = REPO_ROOT / "factory" / "interviews"


def _interview_path(report_id: str) -> Path:
    return INTERVIEW_DIR / f"{report_id}.interview.json"


def _load_interview(report_id: str) -> Interview:
    path = _interview_path(report_id)
    interview = Interview(report_id=report_id)
    if path.exists():
        interview.answers = json.loads(read_text(path)).get("answers", {})
    return interview


def _save_interview(interview: Interview) -> Path:
    path = _interview_path(interview.report_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(
        {"report_id": interview.report_id, "answers": interview.answers,
         "updated_at": datetime.now(timezone.utc).isoformat()},
        indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


# -- commands --------------------------------------------------------------

def cmd_new(report_id: str, title: str) -> int:
    report = Report(f"factory new --id {report_id}")
    if _interview_path(report_id).exists():
        report.fail(f"an interview for {report_id} already exists")
        return report.emit()

    interview = Interview(report_id=report_id)
    interview.answer("purpose", title or "PENDING_APPROVAL")
    _save_interview(interview)

    report.note(f"started a new automation project: {report_id}")
    report.note("")
    report.note("Next, answer the business questions. There are no technical")
    report.note("questions — you describe your work, the Factory does the rest:")
    report.note("")
    for index, question in enumerate(interview.visible_questions(), start=1):
        marker = "done" if question.id in interview.answers else "  ->"
        report.note(f"  {marker} {index}. {question.prompt}")
    report.note("")
    report.note(f"PROJECT_TOOL factory interview --id {report_id} --question grain "
                f"--answer \"...\"")
    return report.emit()


def cmd_interview(report_id: str, question_id: str, answer: str) -> int:
    report = Report(f"factory interview --id {report_id}")
    known = {question.id for question in CORE_QUESTIONS} | {
        "business_key_columns", "approved_categories"}
    if question_id not in known:
        report.fail(f"unknown question {question_id!r}; known: {sorted(known)}")
        return report.emit()

    interview = _load_interview(report_id)
    value: object = answer
    if question_id in ("business_key_columns", "approved_categories", "storage_allowed"):
        value = [part.strip() for part in answer.split(",") if part.strip()]
    interview.answer(question_id, value)
    _save_interview(interview)

    report.note(f"recorded: {question_id}")
    remaining = interview.unanswered_core
    if remaining:
        report.note(f"still to answer ({len(remaining)}): {', '.join(remaining)}")
    else:
        report.note("every core question is answered.")
        report.note(f"Next: PROJECT_TOOL factory review --id {report_id}")
    return report.emit()


def cmd_review(report_id: str) -> int:
    """The Understanding Review — plain language, before any code is written."""
    report = Report(f"factory review --id {report_id}")
    interview = _load_interview(report_id)
    if not interview.answers:
        report.fail(f"no interview found for {report_id}")
        return report.emit()

    contract = interview.technical_contract()
    statuses = {
        s.decision_id: s for s in approvals.status_for(
            report_id, {k: v for k, v in contract.items()
                        if k in ("business_key", "load_mode", "deletion_rule",
                                 "control_total_column", "storage_allowed")})
    }

    print(f"\n  I understand your report as:\n")
    for item in interview.understanding_review():
        print(f"  {item['item']}:")
        print(f"      {item['understanding']}")
        print(f"      ({item['explanation']})")
        print()

    print("  Approval state of each decision:\n")
    for decision_id, status in sorted(statuses.items()):
        label = {"CONFIRMED": "CONFIRMED",
                 "NEEDS_YOUR_APPROVAL": "NEEDS YOUR APPROVAL",
                 "UNKNOWN": "UNKNOWN"}[status.state]
        print(f"    {label:<22} {decision_id}")
        print(f"    {'':<22} {status.detail}")
    print()
    print("  You are approving what these numbers MEAN, not how the software works.")
    print("  Nothing is built for production until the meaning is approved.\n")

    report.note(f"{len(interview.unanswered_core)} core question(s) still unanswered")
    return report.emit()


def cmd_approve(args: argparse.Namespace) -> int:
    """Record a HUMAN approval. An agent running this on its own behalf is a
    Part 41.3 violation, and the identity check below refuses the obvious
    attempts — see factory/approvals.py for the honest trust model."""
    report = Report(f"factory approve --id {args.report_id}")
    interview = _load_interview(args.report_id)
    contract = interview.technical_contract()

    if args.decision not in contract:
        report.fail(f"unknown decision {args.decision!r}; "
                    f"known: {sorted(contract)}")
        return report.emit()

    value = contract[args.decision]
    if value == approvals.SENTINEL:
        report.fail(f"{args.decision} has no value yet — answer the interview "
                    f"question first. An approval must bind to a real value.")
        return report.emit()

    approval = approvals.Approval(
        approval_id=approvals.new_approval_id(args.decision, args.report_id),
        decision_id=args.decision,
        report_id=args.report_id,
        report_version=1,
        approved_value=value,
        value_hash=approvals.value_hash(value),
        human_identity=args.by,
        approved_at=datetime.now(timezone.utc).isoformat(),
        approval_method=args.method,
        evidence_reference=args.evidence,
        notes=args.notes,
    )
    try:
        approvals.record(approval)
    except approvals.ApprovalError as error:
        report.fail(str(error))
        return report.emit()

    synced = approvals.sync_report_toml(args.report_id)

    report.note(f"approved {args.decision} = {value!r}")
    report.note(f"by {args.by} via {args.method}")
    report.note(f"bound to value hash {approval.value_hash[:16]}… — changing the "
                f"value voids this approval automatically")
    if args.decision in synced:
        report.note(f"projected onto reports/{args.report_id}/report.toml "
                    f"[approvals] — PROJECT_TOOL report validate now sees it")
    return report.emit()


def cmd_generate(report_id: str, title: str) -> int:
    report = Report(f"factory generate --id {report_id}")
    interview = _load_interview(report_id)
    if not interview.answers:
        report.fail(f"no interview found for {report_id}")
        return report.emit()

    try:
        project = generate(interview, title=title or report_id)
    except GeneratorError as error:
        report.fail(str(error))
        return report.emit()

    synced = approvals.sync_report_toml(report_id)

    report.note(f"created {project.directory.relative_to(REPO_ROOT)}/")
    for name in project.files_written:
        report.note(f"  wrote {name}")
    report.note("seeded from the Golden Reference, so this report starts from a "
                "known-good, tested shape")
    if synced:
        report.note(f"projected {len(synced)} existing approval(s) onto the new "
                    f"contract: {', '.join(synced)}")
    if project.pending_decisions:
        report.warn(f"{len(project.pending_decisions)} decision(s) still need a "
                    f"named human: {', '.join(project.pending_decisions)}")
    return report.emit()


def cmd_brief(report_id: str) -> int:
    report = Report(f"factory brief --id {report_id}")
    try:
        build_brief.generate(report_id)
    except FileNotFoundError as error:
        report.fail(str(error))
        return report.emit()
    report.note("wrote .ai/BUILD_BRIEF.md")
    report.note("Hand this to the coding agent. It contains the approved contract, "
                "the variation points, the Factory Core boundary and the gates —")
    report.note("and no raw business rows.")
    return report.emit()


def cmd_status(report_id: str | None) -> int:
    report = Report("factory status")
    print(health.render(health.project_health(report_id)))
    if report_id:
        config_path = REPO_ROOT / "reports" / report_id / "report.toml"
        if config_path.exists():
            config = tomllib.loads(read_text(config_path))
            decisions = build_brief._decisions_from(config)
            for status in approvals.status_for(
                    report_id, decisions, mode=config.get("mode", "prototype")):
                if status.state != "CONFIRMED":
                    report.warn(f"{status.decision_id}: {status.state} — {status.detail}")
    return report.emit()


def cmd_validate(report_id: str | None) -> int:
    """Is this project in a state a coding agent should build from?"""
    report = Report("factory validate")
    reports_root = REPO_ROOT / "reports"

    reference = reports_root / "_REFERENCE"
    for required in ("report.toml", "pipeline.toml", "sql/clean.sql",
                     "sql/metrics.sql", "sql/checks.sql"):
        if not (reference / required).exists():
            report.fail(f"Golden Reference is incomplete: missing {required}")

    expected = REPO_ROOT / "tests" / "expected" / "reference" / "expected.json"
    if not expected.exists():
        report.fail("Golden Reference has no frozen expected values")

    targets = ([reports_root / report_id] if report_id
               else [p for p in sorted(reports_root.iterdir())
                     if p.is_dir() and not p.name.startswith("_")])
    for directory in targets:
        config_path = directory / "report.toml"
        if not config_path.exists():
            report.fail(f"{directory.name}: no report.toml")
            continue
        config = tomllib.loads(read_text(config_path))
        decisions = build_brief._decisions_from(config)
        statuses = approvals.status_for(
            directory.name, decisions, mode=config.get("mode", "prototype"))
        unapproved = [s for s in statuses if s.state != "CONFIRMED"]
        if config.get("mode") == "production" and unapproved:
            report.fail(f"{directory.name}: production mode with "
                        f"{len(unapproved)} unapproved decision(s)")
        elif unapproved:
            report.warn(f"{directory.name}: {len(unapproved)} decision(s) await "
                        f"human approval (allowed in {config.get('mode')} mode)")

    if not targets:
        report.note("no employee reports yet — the Golden Reference is the only "
                    "report, which is the expected state for a fresh template")
    return report.emit()


def cmd_reference_verify() -> int:
    """Prove the Golden Reference still produces its known answers."""
    report = Report("factory reference verify")
    try:
        import duckdb  # noqa: F401
    except ImportError:
        report.block("duckdb is not installed. The Golden Reference is application "
                     "tier; install the app dependencies to verify it, or rely on "
                     "the application-tier CI job.")
        return report.emit()

    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.golden.test_reference_pipeline"],
        cwd=REPO_ROOT, capture_output=True, text=True)
    tail = result.stderr.strip().splitlines()[-3:]
    for line in tail:
        report.note(line)
    if result.returncode != 0:
        report.fail("the Golden Reference no longer produces its known answers")
    else:
        report.note("the Golden Reference still produces every known answer")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    command = args.command
    if command == "new":
        return cmd_new(args.report_id, args.title)
    if command == "interview":
        return cmd_interview(args.report_id, args.question, args.answer)
    if command == "review":
        return cmd_review(args.report_id)
    if command == "approve":
        return cmd_approve(args)
    if command == "generate":
        return cmd_generate(args.report_id, args.title)
    if command == "brief":
        return cmd_brief(args.report_id)
    if command == "status":
        return cmd_status(getattr(args, "report_id", None))
    if command == "validate":
        return cmd_validate(getattr(args, "report_id", None))
    if command == "reference":
        if getattr(args, "reference_command", None) == "verify":
            return cmd_reference_verify()
        print("usage error: factory reference verify")
        return EXIT_USAGE
    print(f"usage error: unknown factory command {command!r}")
    return EXIT_USAGE
