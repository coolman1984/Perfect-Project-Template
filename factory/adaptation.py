"""Adaptation evidence, reuse reporting and Universal Core change guard.

Path ownership comes from TEMPLATE_BASELINE.json so an employee copy remains
verifiable without Git history. Legacy report paths remain classified during
migration, but new work is project-centric under projects/<project_id>/.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
from typing import Any

from tools.path_scope import classify_scope, load_baseline, normalize_path


class CoreChangeRequired(RuntimeError):
    pass


def classify_path(path: str) -> str:
    value = normalize_path(path)
    scope = classify_scope(value)
    if scope != "unknown":
        if scope == "presentation":
            return "presentation_config"
        return scope
    # Compatibility classification while legacy report references still exist.
    if value.startswith("reports/"):
        if "/sql/" in value:
            return "business_logic"
        if value.endswith("/dashboard.toml"):
            return "presentation_config"
        return "project_config"
    if re.match(r"^migrations/\d+_.*\.sql$", value):
        return "project_data_shape"
    return "other"


def core_change_guard(paths: list[str], *, reason: str = "") -> list[str]:
    core = [normalize_path(path) for path in paths
            if classify_path(path) in {"universal_core", "tooling"}]
    if core and not reason.strip():
        raise CoreChangeRequired(
            "employee adaptation touched sealed/core-owned files without a master-core justification: "
            + ", ".join(core))
    return core


@dataclass
class RequirementClassification:
    requirement: str
    classification: str
    capability_id: str | None = None
    justification: str = ""


@dataclass
class AdaptationManifest:
    project_id: str
    template: dict[str, Any]
    sources: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    requirements: list[RequirementClassification] = field(default_factory=list)
    core_changes: list[str] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    context_metrics: dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


def manifest_from_project(project_id: str, *, projects_root: Path) -> AdaptationManifest:
    from factory.project_contract import load_project

    project = load_project(projects_root / project_id)
    baseline = load_baseline()
    return AdaptationManifest(
        project_id=project.project_id,
        template={
            "template_id": project.template_id,
            "template_version": project.template_version,
            "sealed": bool(baseline.get("sealed")),
        },
        sources=[source.source_id for source in project.sources],
        relationships=[relationship.relationship_id for relationship in project.relationships],
    )


def write_project_manifest(project_id: str, *, projects_root: Path) -> AdaptationManifest:
    manifest = manifest_from_project(project_id, projects_root=projects_root)
    target = projects_root / project_id / "adaptation_manifest.json"
    target.write_text(json.dumps(manifest.as_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


# ---- legacy compatibility during reports/ -> projects/ migration ----------
DEFAULT_REUSED_CAPABILITIES = (
    "excel.authorized_com", "data.staging_lineage", "history.standard_modes",
    "quality.reconciliation", "analytics.sql_metrics", "dashboard.configured",
    "runtime.loopback", "ai.map_context",
)


@dataclass
class LegacyReportManifest:
    report_id: str
    department: str = "PENDING_APPROVAL"
    purpose: str = "PENDING_APPROVAL"
    sources: list[str] = field(default_factory=list)
    grain: str = "PENDING_APPROVAL"
    business_keys: list[str] = field(default_factory=list)
    update_strategy: str = "PENDING_APPROVAL"
    kpis: list[str] = field(default_factory=list)
    dashboard_components: list[str] = field(default_factory=list)
    core_modules_reused: list[str] = field(default_factory=lambda: list(DEFAULT_REUSED_CAPABILITIES))
    custom_logic_added: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def reuse_indicator(self) -> int:
        # Kept only for backward-compatible tests/UI. New reuse reports must not
        # use this percentage as acceptance evidence.
        total = len(self.core_modules_reused) + len(self.custom_logic_added)
        return 100 if total == 0 else round(len(self.core_modules_reused) / total * 100)


def manifest_from_report(report_id: str, *, reports_root: Path,
                         department: str = "PENDING_APPROVAL") -> LegacyReportManifest:
    import tomllib
    directory = reports_root / report_id
    report = tomllib.loads((directory / "report.toml").read_text("utf-8"))
    dashboard = tomllib.loads((directory / "dashboard.toml").read_text("utf-8")) \
        if (directory / "dashboard.toml").exists() else {}
    history = report.get("history", {})
    excel = report.get("excel", {})
    sql = sorted(str(path.relative_to(directory)) for path in (directory / "sql").glob("*.sql")) \
        if (directory / "sql").exists() else []
    return LegacyReportManifest(
        report_id, department,
        str(report.get("output", {}).get("audience", report_id)),
        [f"{key}: {excel[key]}" for key in ("sheet", "data_area") if excel.get(key)],
        "PENDING_APPROVAL", [str(x) for x in history.get("business_key", [])],
        str(report.get("load_mode", "PENDING_APPROVAL")),
        [f"{item.get('id')}: {item.get('label', item.get('id'))}" for item in dashboard.get("kpis", [])],
        [f"{item.get('type', 'chart')}: {item.get('id')}" for item in dashboard.get("charts", [])],
        list(DEFAULT_REUSED_CAPABILITIES), sql,
    )


def write_manifest(report_id: str, *, reports_root: Path,
                   department: str = "PENDING_APPROVAL") -> LegacyReportManifest:
    manifest = manifest_from_report(report_id, reports_root=reports_root, department=department)
    directory = reports_root / report_id
    (directory / "adaptation_manifest.json").write_text(
        json.dumps(manifest.as_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (directory / "adaptation_manifest.md").write_text(
        f"# Legacy Adaptation Manifest — {report_id}\n\n"
        "This compatibility artifact is report-centric and is not the V8.1 project-pack contract. "
        "Migrate new work to `projects/<project_id>/`.\n", encoding="utf-8")
    return manifest
