"""Generate a compact AI adaptation brief without raw confidential rows."""
from __future__ import annotations
import tomllib
from pathlib import Path
from factory import adaptation, approvals
from factory.questionnaire import HUMAN_OWNED

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIEF_PATH = REPO_ROOT / ".ai" / "BUILD_BRIEF.md"

VARIATION_POINTS = (
    ("reports/<id>/report.toml", "source/history/quality contract"),
    ("reports/<id>/pipeline.toml", "columns/tables/SQL wiring"),
    ("reports/<id>/dashboard.toml", "KPIs, filters, charts and insight patterns"),
    ("reports/<id>/sql/clean.sql", "typing/normalization/reject rules"),
    ("reports/<id>/sql/checks.sql", "control-total queries"),
    ("reports/<id>/sql/metrics.sql", "trusted KPI calculations"),
    ("reports/<id>/sql/insights.sql", "evidence queries"),
    ("migrations/NNNN_*.sql", "business table shape"),
)
FACTORY_CORE = (
    ("app/pipeline.py", "Universal run order"),
    ("app/excel/", "authorized extraction"),
    ("app/data/", "staging/history/archive"),
    ("app/quality/", "quality/reconciliation"),
    ("app/analytics/configured.py", "configured SQL analytics"),
    ("app/dashboard/json_builder.py", "configured dashboard package"),
    ("factory/source_profile.py", "compact profiling"),
    ("factory/adaptation.py", "reuse/core guard"),
)


def generate(report_id: str, *, root: Path | None = None) -> str:
    base = root or REPO_ROOT
    directory = base / "reports" / report_id
    config = tomllib.loads((directory / "report.toml").read_text("utf-8"))
    decisions = _decisions_from(config)
    statuses = approvals.status_for(
        report_id, decisions, mode=config.get("mode", "prototype"))
    confirmed = [status for status in statuses if status.state == "CONFIRMED"]
    pending = [status for status in statuses if status.state != "CONFIRMED"]
    manifest = adaptation.manifest_from_report(
        report_id, reports_root=base / "reports")

    lines = [
        f"# BUILD BRIEF — {report_id}", "", "## Mission", "",
        "The application already exists. Teach the Universal Excel Automation "
        "Engine what this Excel process means. Do not build another application.",
        "", "Normal order: `PROFILE -> MAP -> CONFIGURE -> SMALL BUSINESS LOGIC -> TEST`.",
        "", "## Approved business decisions", "",
    ]
    lines += [
        f"- {status.decision_id}: `{decisions[status.decision_id]}` — {status.approved_by}"
        for status in confirmed
    ] or ["- none"]
    lines += ["", "## Pending human meaning", ""]
    lines += [
        f"- {status.decision_id}: {status.state} — {status.detail}"
        for status in pending
    ] or ["- none"]
    lines += [
        "", "## Reuse first", "",
        f"- Capability-level reuse indicator: **{manifest.reuse_indicator()}%** "
        "(directional, not exact code math)",
        "- Start with `reports/_REFERENCE/` for full-pipeline patterns. Copy its "
        "pattern; configure and extend it. **Do not redesign it.**",
        "- Use `reports/line_downtime/` as proof that a different business shape "
        "uses the same core.",
        "", "## Variation points — files you normally change", "",
        "| Variation point | What belongs there |", "|---|---|",
    ]
    lines += [f"| `{path}` | {why} |" for path, why in VARIATION_POINTS]
    lines += [
        "", "### Universal Core (legacy name: Factory Core) — normally unchanged", "",
        "| Shared area | Why |", "|---|---|",
    ]
    lines += [f"| `{path}` | {why} |" for path, why in FACTORY_CORE]
    lines += [
        "",
        "Do not redesign it for a normal report. If Core must change, explain why "
        "configuration is insufficient and keep both references green.",
        "", "## Required verification", "",
        "```text",
        "python3 -m unittest discover -s tests -t .",
        "PROJECT_TOOL report validate --mode production",
        "PROJECT_TOOL map verify",
        "PROJECT_TOOL architecture verify --source-scan",
        "PROJECT_TOOL gates status",
        "```",
        "",
        "At minimum preserve `GATE_CONTROL_TOTAL`, `GATE_HISTORY_IDEMPOTENT`, "
        "`GATE_INSIGHT_EVIDENCE`, and `GATE_DASHBOARD_CONTRACT`. A real protected "
        "Excel/COM proof remains conditional until it runs on the authorized Windows PC.",
        "",
    ]
    text = "\n".join(lines)
    target = base / ".ai" / "BUILD_BRIEF.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return text


def _decisions_from(config: dict) -> dict:
    history = config.get("history", {})
    quality = config.get("quality", {})
    output = config.get("output", {})
    found = {
        "business_key": history.get("business_key"),
        "load_mode": config.get("load_mode"),
        "lookback_days": history.get("lookback_days"),
        "deletion_rule": history.get("deletion_rule"),
        "control_total_column": quality.get("control_total_column"),
        "storage_allowed": output.get("storage_allowed"),
    }
    return {key: value for key, value in found.items() if key in HUMAN_OWNED or key in found}
