"""Generate controlled report variation points from a business interview."""
from __future__ import annotations
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from factory import adaptation
from factory.questionnaire import Interview

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_ROOT = REPO_ROOT / "reports"
REFERENCE_DIR = REPORTS_ROOT / "_REFERENCE"
TEMPLATE_DIR = REPORTS_ROOT / "_TEMPLATE"
SENTINEL = "PENDING_APPROVAL"


class GeneratorError(RuntimeError):
    pass


@dataclass
class GeneratedProject:
    report_id: str
    directory: Path
    files_written: list[str]
    pending_decisions: list[str]

    @property
    def ready_for_production(self) -> bool:
        return not self.pending_decisions


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(f'\"{str(item)}\"' for item in value) + "]"
    return f'\"{value}\"'


def generate(
    interview: Interview, *, title: str, reports_root: Path | None = None,
    seed_from_reference: bool = True,
) -> GeneratedProject:
    root = reports_root or REPORTS_ROOT
    destination = root / interview.report_id
    if destination.exists():
        raise GeneratorError(f"reports/{interview.report_id}/ already exists")
    source = REFERENCE_DIR if seed_from_reference else TEMPLATE_DIR
    if not source.exists():
        raise GeneratorError(f"missing seed project: {source}")
    shutil.copytree(source, destination)
    contract = interview.technical_contract()
    written: list[str] = []

    (destination / "report.toml").write_text(
        _render_report_toml(interview, contract, title), encoding="utf-8")
    written.append("report.toml")
    (destination / "report_definition.md").write_text(
        _render_definition(interview, contract, title), encoding="utf-8")
    written.append("report_definition.md")
    adaptation.write_manifest(interview.report_id, reports_root=root)
    written += ["adaptation_manifest.json", "adaptation_manifest.md"]
    pending = sorted(key for key, value in contract.items() if value == SENTINEL)
    return GeneratedProject(interview.report_id, destination, written, pending)


def _render_report_toml(interview: Interview, contract: dict, title: str) -> str:
    reference = (REFERENCE_DIR / "report.toml").read_text("utf-8")
    lines = [
        f"# {title}",
        "# Generated from business meaning. Configure/adapt; do not rebuild Universal Core.",
        "", f'report_id      = "{interview.report_id}"', "report_version = 1",
        'mode           = "prototype"',
        f"load_mode      = {_toml_value(contract['load_mode'])}",
        'timezone       = "PENDING_APPROVAL"', 'currency       = "PENDING_APPROVAL"', "",
    ]
    inside_excel = False
    for line in reference.splitlines():
        if line.startswith("[excel]"):
            inside_excel = True
        elif line.startswith("[history]"):
            inside_excel = False
        if inside_excel:
            lines.append(line.replace('adapter = "fixture"', 'adapter = "com"')
                         .replace('adapter               = "fixture"', 'adapter               = "com"'))
    lines += [
        "", "[history]", f"business_key   = {_toml_value(contract['business_key'])}",
        'event_date     = "PENDING_APPROVAL"',
        f"lookback_days  = {_toml_value(contract['lookback_days'])}",
        f"deletion_rule  = {_toml_value(contract['deletion_rule'])}",
        "", "[quality]", "required_columns_block   = true",
        "max_duplicate_key_rate   = 0.0", "max_required_null_rate   = 0.0",
        'max_row_count_change_pct = "PENDING_APPROVAL"',
        f"control_total_column     = {_toml_value(contract['control_total_column'])}",
        "non_negative_columns     = []", "approved_categories      = []",
        "", "[output]", f"audience             = {_toml_value(contract.get('purpose', SENTINEL))}",
        f"storage_allowed      = {_toml_value(contract['storage_allowed'])}",
        'retention_days       = "PENDING_APPROVAL"', "ai_narrative_allowed = false",
        "", "[approvals]",
    ]
    for key in ("business_key", "load_mode", "deletion_rule", "control_total_column", "storage_allowed"):
        lines.append(f'{key} = {{ approved_by = "", approved_at = "", evidence = "" }}')
    return "\n".join(lines) + "\n"


def _render_definition(interview: Interview, contract: dict, title: str) -> str:
    rows = "\n".join(
        f"| {item['item']} | {item['understanding']} | {item['explanation']} |"
        for item in interview.understanding_review()
    )
    return (
        f"# Report definition — {title}\n\n"
        "> Generated from the business interview. The employee approves the meaning "
        "below, not the implementation.\n\n"
        "| Item | Understanding | What this means |\n|---|---|---|\n"
        f"{rows}\n\n"
        "## Adaptation rule\n\n"
        "Profile the Excel source, then adapt this report's mapping/configuration/"
        "business SQL and dashboard.toml. Universal Core changes only when a "
        "genuinely reusable capability is missing.\n"
    )
