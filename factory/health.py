"""Project health an employee can read (brief §16).

Every status here DERIVES from real gate evidence. There are no invented
percentages: "Understanding 8/10 confirmed" is a count of approved decisions,
and "Data access Ready" is a gate that actually passed.

Clicking an item must explain what it means, why it matters, what remains and
who needs to act — so each status carries all four.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from factory import approvals
from factory.build_brief import _decisions_from

REPO_ROOT = Path(__file__).resolve().parent.parent

READY, PARTIAL, PENDING, BLOCKED = "Ready", "Partial", "Pending", "Blocked"


@dataclass(frozen=True)
class HealthItem:
    area: str
    status: str
    summary: str
    what_it_means: str
    why_it_matters: str
    what_remains: str
    who_acts: str


def _gate_status(gates: list[dict], gate_id: str) -> str:
    for gate in gates:
        if gate.get("id") == gate_id:
            return gate.get("status", "not_started")
    return "not_started"


def _from_gate(status: str) -> str:
    return {"pass": READY, "conditional": PENDING, "fail": BLOCKED,
            "not_applicable": READY}.get(status, PENDING)


def project_health(report_id: str | None = None, *, root: Path | None = None) -> list[HealthItem]:
    """One simple health model for the whole automation."""
    base = root or REPO_ROOT
    items: list[HealthItem] = []

    # -- understanding, from real approvals --------------------------------
    if report_id:
        config_path = base / "reports" / report_id / "report.toml"
        if config_path.exists():
            config = tomllib.loads(config_path.read_text("utf-8"))
            decisions = _decisions_from(config)
            statuses = approvals.status_for(
                report_id, decisions, mode=config.get("mode", "prototype"))
            confirmed = sum(1 for s in statuses if s.state == "CONFIRMED")
            total = len(statuses)
            outstanding = [s.decision_id for s in statuses if s.state != "CONFIRMED"]
            items.append(HealthItem(
                area="Understanding",
                status=READY if confirmed == total else PARTIAL,
                summary=f"{confirmed}/{total} confirmed",
                what_it_means="How much of your report's business meaning a named "
                              "person has approved.",
                why_it_matters="The system refuses to run in production while any "
                               "meaning is unapproved, because a guessed business "
                               "rule is the most expensive kind of mistake.",
                what_remains=(", ".join(outstanding) if outstanding
                              else "Nothing — every decision is approved."),
                who_acts="The report's business owner." if outstanding else "Nobody.",
            ))

    # -- everything else, from the gate ledger -----------------------------
    try:
        from tools import gates as gates_module
        ledger = gates_module.load_ledger()
    except Exception:  # noqa: BLE001 — health must never crash the UI
        ledger = []

    mapping = [
        ("Data access", "GATE_PROTECTED_FILE_PROOF",
         "Whether the system has proved it can read your real protected files.",
         "Until this passes on your own PC with your own files, extraction is "
         "only proven against synthetic test data.",
         "Run once on a Windows PC with Excel and the real files.",
         "You, with IT if the files are locked down."),
        ("Accuracy checks", "GATE_CONTROL_TOTAL",
         "Whether the number you use to check the report matches exactly.",
         "This is what makes a dashboard number safe to present to management.",
         "Confirm your check number, then process one real file.",
         "The business owner confirms the number; the system does the rest."),
        ("History", "GATE_HISTORY_IDEMPOTENT",
         "Whether processing the same file twice is safe.",
         "Without it, a repeated upload silently doubles your totals.",
         "Proven on the reference project; repeat on your own report.",
         "Nobody — the system proves this automatically."),
        ("Dashboard", "GATE_DASHBOARD_CONTRACT",
         "Whether the dashboard shows exactly what the database holds.",
         "Stops the page from drifting away from the trusted numbers.",
         "Build the report's dashboard and run the browser checks.",
         "Nobody — automatic."),
        ("Offline package", "GATE_RELEASE_COMPLETENESS",
         "Whether the app can be copied to a PC and just run.",
         "The employee should never install anything.",
         "Build the release and verify it offline.",
         "Whoever prepares the release."),
        ("Corporate PC proof", "GATE_CLEAN_OFFLINE_MACHINE",
         "Whether it has been proven on a real company computer.",
         "A cloud test cannot prove your company's own security policy.",
         "Run the clean-PC sequence on a representative machine.",
         "You, with IT."),
    ]
    for area, gate_id, meaning, matters, remains, actor in mapping:
        status = _gate_status(ledger, gate_id)
        items.append(HealthItem(
            area=area, status=_from_gate(status),
            summary={"pass": "Proven", "conditional": "Needs a real PC",
                     "fail": "Failing"}.get(status, "Not started yet"),
            what_it_means=meaning, why_it_matters=matters,
            what_remains=("Nothing." if status == "pass" else remains),
            who_acts=("Nobody." if status == "pass" else actor),
        ))
    return items


def render(items: list[HealthItem]) -> str:
    width = max((len(item.area) for item in items), default=10)
    lines = ["", "  PROJECT HEALTH", "  " + "-" * (width + 24)]
    for item in items:
        lines.append(f"  {item.area:<{width}}  {item.status:<8} {item.summary}")
    lines.append("")
    lines.append("  Every status above comes from a real gate or a real approval.")
    lines.append("  Nothing here is an estimate.")
    return "\n".join(lines)
