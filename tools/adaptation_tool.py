#!/usr/bin/env python3
"""Stable V8.1 project-adaptation commands for copied employee folders."""
from __future__ import annotations

import argparse
import json

from factory.adaptation import write_project_manifest
from factory.project_contract import (
    ProjectContractError, find_project_directory, load_project)
from factory.project_generator import ProjectGeneratorError, start_project
from factory.reuse_report import build_reuse_report
from tools._common import EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report
from tools.template_baseline import verify as verify_baseline

PROJECTS_ROOT = REPO_ROOT / "projects"


def new(project_id: str, title: str = "") -> int:
    report = Report(f"adaptation new --project {project_id}")
    try:
        directory = start_project(
            project_id, title=title, projects_root=PROJECTS_ROOT)
    except ProjectGeneratorError as error:
        report.fail(str(error))
        return report.emit()
    report.note(f"created project-owned discovery pack: {directory.relative_to(REPO_ROOT)}")
    report.note(
        "next: answer business questions and profile every source; the generator "
        "did not clone source/KPI/history assumptions from a reference project")
    return report.emit()


def _load(project_id: str):
    directory = find_project_directory(PROJECTS_ROOT, project_id)
    return directory, load_project(directory)


def validate(project_id: str) -> int:
    report = Report(f"adaptation validate --project {project_id}")
    try:
        directory, project = _load(project_id)
    except ProjectContractError as error:
        report.fail(str(error))
        return report.emit()
    report.note(
        f"project {project.project_id}: {len(project.sources)} source(s), "
        f"{len(project.relationships)} relationship(s)")
    pending = [
        relationship.relationship_id
        for relationship in project.relationships
        if relationship.approval_state != "CONFIRMED"
    ]
    if pending:
        report.warn(
            "relationships need business approval: " + ", ".join(pending))
    else:
        report.note("all declared relationships are confirmed")
    write_project_manifest(project_id, projects_root=directory.parent)
    return report.emit()


def core_guard(project_id: str) -> int:
    # On an employee copy, the sealed baseline is the authority and works with
    # no Git history. An unsealed master-development branch intentionally blocks.
    code = verify_baseline()
    if code != EXIT_PASS:
        return code
    report = Report(f"adaptation core-guard --project {project_id}")
    try:
        _load(project_id)
    except ProjectContractError as error:
        report.fail(str(error))
        return report.emit()
    report.note(
        "sealed Universal Core matches baseline; project-owned adaptation may proceed")
    return report.emit()


def reuse_report(project_id: str) -> int:
    report = Report(f"adaptation reuse-report --project {project_id}")
    try:
        directory, project = _load(project_id)
        # Pass the declared project_id, never the directory name: a reference
        # pack lives in projects/_REFERENCE_FINANCE_PPV but declares
        # reference_finance_ppv, and the directory name is not a valid
        # identifier.
        payload = build_reuse_report(
            project.project_id, projects_root=directory.parent)
    except (FileNotFoundError, ProjectContractError) as error:
        report.fail(str(error))
        return report.emit()
    target = directory / "reuse_report.json"
    target.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    report.note(f"wrote {target.relative_to(REPO_ROOT)}")
    report.note(
        f"core files changed: {len(payload['core_files_changed'])}; "
        f"project config: {len(payload['project_config_files_changed'])}; "
        f"business logic: {len(payload['business_logic_files_changed'])}")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command == "new":
        return new(args.project_id, getattr(args, "title", ""))
    if args.command == "validate":
        return validate(args.project_id)
    if args.command == "core-guard":
        return core_guard(args.project_id)
    if args.command == "reuse-report":
        return reuse_report(args.project_id)
    return EXIT_FAIL
