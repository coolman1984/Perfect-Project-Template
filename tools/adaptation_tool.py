#!/usr/bin/env python3
"""Stable project-adaptation commands for copied employee folders."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from factory.adaptation import core_change_guard, write_project_manifest
from factory.project_contract import ProjectContractError, load_project
from factory.reuse_report import build_reuse_report
from tools._common import EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report
from tools.template_baseline import verify as verify_baseline

PROJECTS_ROOT=REPO_ROOT/"projects"


def validate(project_id: str) -> int:
    report=Report(f"adaptation validate --project {project_id}")
    try: project=load_project(PROJECTS_ROOT/project_id)
    except ProjectContractError as error: report.fail(str(error)); return report.emit()
    report.note(f"project {project.project_id}: {len(project.sources)} source(s), {len(project.relationships)} relationship(s)")
    pending=[r.relationship_id for r in project.relationships if r.approval_state!="CONFIRMED"]
    if pending: report.warn("relationships need business approval: "+", ".join(pending))
    else: report.note("all declared relationships are confirmed")
    write_project_manifest(project_id,projects_root=PROJECTS_ROOT)
    return report.emit()


def core_guard(project_id: str) -> int:
    # On an employee copy, the sealed baseline is the authoritative proof and
    # works without Git. An unsealed development master intentionally blocks.
    code=verify_baseline()
    if code!=EXIT_PASS: return code
    report=Report(f"adaptation core-guard --project {project_id}")
    try: load_project(PROJECTS_ROOT/project_id)
    except ProjectContractError as error: report.fail(str(error)); return report.emit()
    report.note("sealed Universal Core matches baseline; project-owned adaptation may proceed")
    return report.emit()


def reuse_report(project_id: str) -> int:
    report=Report(f"adaptation reuse-report --project {project_id}")
    try: payload=build_reuse_report(project_id,projects_root=PROJECTS_ROOT)
    except (FileNotFoundError,ProjectContractError) as error: report.fail(str(error)); return report.emit()
    target=PROJECTS_ROOT/project_id/"reuse_report.json"; target.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report.note(f"wrote {target.relative_to(REPO_ROOT)}")
    report.note(f"core files changed: {len(payload['core_files_changed'])}; project config: {len(payload['project_config_files_changed'])}; business logic: {len(payload['business_logic_files_changed'])}")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command=="validate": return validate(args.project_id)
    if args.command=="core-guard": return core_guard(args.project_id)
    if args.command=="reuse-report": return reuse_report(args.project_id)
    return EXIT_FAIL
