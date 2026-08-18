"""Create a new V8.1 employee project pack without cloning a department demo.

The generator creates only project-owned variation points. It never copies or
modifies Universal Core. Sources/relationships remain deliberately incomplete
until the business interview + source profiling establish their meaning.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from factory.project_contract import ID
from factory.project_questionnaire import PROJECT_QUESTIONS
from tools._common import REPO_ROOT, sha256_file
from tools.path_scope import load_baseline

PROJECTS_ROOT = REPO_ROOT / "projects"
SECURITY_POLICY = "policy/security_policy.toml"


class ProjectGeneratorError(RuntimeError):
    pass


def _quoted(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def start_project(
    project_id: str,
    *,
    title: str = "",
    projects_root: Path | None = None,
) -> Path:
    """Create the controlled project-owned setup surface.

    This is intentionally not yet a runnable project. A runnable project starts
    only after source roles, schemas, keys, relationships, controls and trusted
    calculations are understood/approved. PENDING setup is safer than copying
    the Golden Reference and hoping its assumptions happen to match Finance.
    """
    if not ID.fullmatch(project_id):
        raise ProjectGeneratorError(
            "project_id must be lower_snake_case starting with a letter")
    root = projects_root or PROJECTS_ROOT
    destination = root / project_id
    if destination.exists():
        raise ProjectGeneratorError(
            f"projects/{project_id}/ already exists")
    baseline = load_baseline()
    baseline_path = REPO_ROOT / "TEMPLATE_BASELINE.json"
    destination.mkdir(parents=True)
    (destination / "business_rules").mkdir()
    (destination / "presentation").mkdir()

    display_title = title.strip() or project_id.replace("_", " ").title()
    (destination / "project.toml").write_text(
        "\n".join([
            f"project_id = {_quoted(project_id)}",
            "project_version = 1",
            'mode = "discovery"',
            "outputs = []",
            "",
            "[template]",
            f"template_id = {_quoted(str(baseline.get('template_id', 'unknown')))}",
            f"template_version = {_quoted(str(baseline.get('template_version', 'unknown')))}",
            f"baseline_digest = {_quoted(sha256_file(baseline_path))}",
            "",
            "[business]",
            'purpose = "PENDING_APPROVAL"',
            'owner = "PENDING_APPROVAL"',
            'decision = "PENDING_APPROVAL"',
            "",
            "[security]",
            f"policy = {_quoted(SECURITY_POLICY)}",
            "",
            "[setup]",
            f"title = {_quoted(display_title)}",
            'status = "BUSINESS_DISCOVERY"',
        ]) + "\n",
        encoding="utf-8",
    )
    (destination / "sources.toml").write_text(
        "# Generated empty on purpose. AI fills one [[sources]] block per approved source role.\n"
        "# Do not copy source assumptions from a reference project.\n",
        encoding="utf-8",
    )
    (destination / "relationships.toml").write_text(
        "# Joins are never inferred from matching column names.\n"
        "relationships = []\n",
        encoding="utf-8",
    )
    (destination / "dashboard.toml").write_text(
        "[meta]\n"
        f"title = {_quoted(display_title)}\n"
        "# KPI/chart bindings are added only after business meaning is approved.\n",
        encoding="utf-8",
    )
    (destination / "business_rules" / "README.md").write_text(
        "# Project-specific business logic\n\n"
        "Keep only genuinely project-specific trusted SQL/Python here. Prefer "
        "reusable capabilities first. Never duplicate a trusted formula in SQL, "
        "Python and browser code.\n",
        encoding="utf-8",
    )
    setup = {
        "schema_version": 1,
        "project_id": project_id,
        "status": "BUSINESS_DISCOVERY",
        "questions": [
            {
                "id": question.id,
                "prompt": question.prompt,
                "why": question.why,
                "answer": None,
                "approval_state": "UNKNOWN",
            }
            for question in PROJECT_QUESTIONS
        ],
        "source_profiles": [],
        "note": (
            "Answers contain business meaning only. Corporate storage, retention "
            "and external-AI rules come from the IT/Security policy."),
    }
    (destination / "setup_answers.json").write_text(
        json.dumps(setup, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination
