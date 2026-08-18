"""Generate the low-token project work package for an adaptation agent.

The brief contains approved structure, source roles, relationships, capability
entry points, pending meaning and verification targets. It deliberately omits
raw business rows and protected sample values.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from factory.adaptation import manifest_from_project
from factory.project_contract import find_project_directory, load_project
from tools._common import REPO_ROOT
from tools.path_scope import load_baseline

CAPABILITY_PATH = REPO_ROOT / "capabilities" / "registry.json"
CONTEXT_METRICS = REPO_ROOT / "workspace" / "context_metrics.json"
GLOBAL_BRIEF = REPO_ROOT / ".ai" / "BUILD_BRIEF.md"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError:
        return default


def build_project_brief(
    project_id: str,
    *,
    projects_root: Path | None = None,
) -> str:
    root = projects_root or (REPO_ROOT / "projects")
    directory = find_project_directory(root, project_id)
    project = load_project(directory)
    baseline = load_baseline()
    manifest = manifest_from_project(
        project_id, projects_root=directory.parent)
    registry = _load_json(CAPABILITY_PATH, {"capabilities": []})
    metrics = _load_json(CONTEXT_METRICS, {})

    lines = [
        f"# BUILD BRIEF — {project.project_id}",
        "",
        "> Generated project context. No raw business rows are included.",
        "",
        "## Mission",
        "",
        "Adapt the already-built Universal Excel Automation Engine to this "
        "project. Reuse capabilities first. Do not redesign technical "
        "architecture unless a missing reusable capability is proven.",
        "",
        "## Template integrity",
        "",
        f"- Template ID: `{project.template_id}`",
        f"- Project template version: `{project.template_version}`",
        f"- Current baseline sealed: `{bool(baseline.get('sealed'))}`",
        "- Employee mode requires `PROJECT_TOOL template-baseline verify` PASS.",
        "- Master-core development may remain unsealed until release.",
        "",
        "## Source roles",
        "",
        "| Source | Role | Required | Grain | Key | History | Controls |",
        "|---|---|---|---|---|---|---|",
    ]
    for source in project.sources:
        lines.append(
            f"| `{source.source_id}` | {source.role} | "
            f"{'yes' if source.required else 'no'} | {source.grain} | "
            f"`{', '.join(source.business_key)}` | {source.load_mode} | "
            f"{', '.join(source.control_totals) or 'none'} |")

    lines += ["", "## Relationships", ""]
    if not project.relationships:
        lines.append("- None declared.")
    for relationship in project.relationships:
        lines.append(
            f"- `{relationship.relationship_id}`: "
            f"`{relationship.left_source}` ({', '.join(relationship.left_keys)}) "
            f"→ `{relationship.right_source}` "
            f"({', '.join(relationship.right_keys)}), "
            f"{relationship.cardinality}, {relationship.join_type}, "
            f"approval=`{relationship.approval_state}`, "
            f"match_required=`{relationship.require_match}`.")

    lines += [
        "",
        "## Requirement classification",
        "",
        "Every requirement must be one of:",
        "",
        "```text",
        "REUSE_AS_IS",
        "CONFIGURE",
        "PROJECT_SPECIFIC_BUSINESS_LOGIC",
        "NEW_REUSABLE_CAPABILITY_CANDIDATE",
        "```",
        "",
        "## Reusable capabilities to check before opening core source",
        "",
        "Machine source: `capabilities/registry.json`. The entries below are a "
        "routed summary; the registry stays authoritative for full definitions.",
        "",
    ]
    for capability in registry.get("capabilities", []):
        entry_points = capability.get("config_entry_points", [])
        lines.append(
            f"- `{capability.get('id')}` — {capability.get('purpose', '')} "
            f"Config: {', '.join(entry_points) or 'none'}. "
            f"Limitations: {'; '.join(capability.get('limitations', [])) or 'none'}")

    pending = [
        relationship.relationship_id
        for relationship in project.relationships
        if relationship.approval_state != "CONFIRMED"
    ]
    lines += [
        "",
        "## Human / policy boundary",
        "",
        f"- Relationship approvals still pending: "
        f"{', '.join(pending) if pending else 'none'}.",
        "- Business meanings, keys, trusted totals, source precedence and KPI "
        "definitions require human approval.",
        "- Storage/retention/external-AI rules come from "
        "`policy/security_policy.toml`; the employee is not asked to invent them.",
        "- Source profiling is metadata-only unless IT/Security policy explicitly "
        "permits sample values.",
        "",
        "## Variation points you may edit",
        "",
        f"- `{directory.relative_to(REPO_ROOT)}/project.toml`",
        f"- `{directory.relative_to(REPO_ROOT)}/sources.toml`",
        f"- `{directory.relative_to(REPO_ROOT)}/relationships.toml`",
        f"- `{directory.relative_to(REPO_ROOT)}/dashboard.toml`",
        f"- `{directory.relative_to(REPO_ROOT)}/business_rules/`",
        f"- `tests/projects/{project.project_id}/`",
        "",
        "## Universal Core is not a normal adaptation surface",
        "",
        "Core ownership is defined by `TEMPLATE_BASELINE.json`, not this prose. "
        "If a core edit appears necessary, run the core guard and document why "
        "configuration or an existing extension point cannot express the need.",
        "",
        "## Required proof before done",
        "",
        "```text",
        "PROJECT_TOOL adaptation validate --project " + project.project_id,
        "PROJECT_TOOL adaptation reuse-report --project " + project.project_id,
        "PROJECT_TOOL map verify",
        "PROJECT_TOOL architecture verify --source-scan",
        "PROJECT_TOOL constitution audit",
        "PROJECT_TOOL gates status",
        "```",
        "",
        "Project-specific tests must also prove source reconciliation, rerun "
        "safety, corrections, blocking failure preservation, relationships and "
        "trusted outputs.",
        "",
        "## Context measurement",
        "",
        f"- Estimated routed tokens: `{metrics.get('estimated_tokens', 'not measured')}`",
        f"- Routed files: `{metrics.get('files_selected', 'not measured')}`",
        f"- Routed bytes: `{metrics.get('bytes_selected', 'not measured')}`",
        f"- Context expansions: `{metrics.get('expansions', 'not measured')}`",
        f"- Provider-reported tokens: `{metrics.get('provider_tokens', 'not available')}`",
        "",
        "## Manifest snapshot",
        "",
        f"- Sources: {', '.join(manifest.sources)}",
        f"- Relationships: {', '.join(manifest.relationships) or 'none'}",
        "",
    ]
    return "\n".join(lines)


def write_project_brief(
    project_id: str,
    *,
    projects_root: Path | None = None,
) -> tuple[Path, Path]:
    root = projects_root or (REPO_ROOT / "projects")
    directory = find_project_directory(root, project_id)
    content = build_project_brief(project_id, projects_root=root)
    project_brief = directory / "BUILD_BRIEF.md"
    project_brief.write_text(content, encoding="utf-8")
    GLOBAL_BRIEF.parent.mkdir(parents=True, exist_ok=True)
    GLOBAL_BRIEF.write_text(content, encoding="utf-8")
    return project_brief, GLOBAL_BRIEF
