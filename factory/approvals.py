"""Human approval provenance (Constitution Part 41, strengthened).

## The trust model, stated honestly

An AI agent working in this repository has write access to every file,
including this approval store. **Nothing here is cryptographic proof against a
determined malicious agent**, and claiming otherwise would be worse than
claiming nothing — it would invite people to trust a control that cannot bear
the weight.

What this store *does* provide, and what it is worth:

| Property | Strength | Why it matters |
|---|---|---|
| Explicit provenance | strong | Every approved value names a human, a time, a method and an evidence reference. A reviewer can audit the whole chain in one file. |
| **Value binding** | strong | The approval records a hash of the exact approved value. Change the configuration afterwards and the approval is automatically void. An agent cannot approve `X` and then quietly ship `Y`. |
| Method allow-list | moderate | Only recognised human actions count. `agent`, `ai`, `assistant`, `automated` and similar identities are rejected outright. |
| Tamper resistance | **weak by design** | A hostile agent with write access can forge a record. That is why the strong assurance options below exist. |

## Stronger assurance, when an organisation needs it

The value binding above makes forgery *detectable in review*, not impossible.
For genuine organisational assurance, pair this store with one of:

    human-reviewed pull request     the approval diff is reviewed by a person
    signed approval artifact        detached signature over the approval record
    protected approval store        a location the build agent cannot write to
    company identity workflow       approval recorded in an external system

None of these require internet access at runtime — they are review-time and
build-time controls (Part 43).

## What an agent may and may not do

An agent MAY: propose values, explain trade-offs, write `PENDING_APPROVAL`,
prepare candidates, and mark them `SUGGESTED — HUMAN APPROVAL REQUIRED`.

An agent MAY NOT: approve, invent an approver, silently resolve
`PENDING_APPROVAL`, or record its own proposal as human-confirmed.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APPROVALS_DIR = Path(__file__).resolve().parent / "approvals"

#: Recognised human approval actions. Anything else is refused.
VALID_METHODS = frozenset({
    "wizard_confirmation",   # the person clicked Approve in the setup review
    "signed_artifact",       # detached signature over the approval record
    "pull_request_review",   # a human approved the diff that carries this value
    "external_workflow",     # recorded in a company identity/approval system
    "fixture",               # synthetic test data; never valid in production
})

#: Identities that are not human. Refused so an agent cannot name itself.
FORBIDDEN_IDENTITY = re.compile(
    r"\b(ai|agent|assistant|claude|gpt|copilot|bot|automation|automated|system|"
    r"llm|model|script)\b", re.IGNORECASE)

SENTINEL = "PENDING_APPROVAL"


class ApprovalError(ValueError):
    """The approval is malformed, or something tried to bypass the boundary."""


def canonical_value(value: Any) -> str:
    """Stable text for hashing an approved value.

    Sorting keys and normalising separators means a cosmetic reformat of the
    configuration does not void a legitimate approval, while a genuine change
    of meaning always does.
    """
    if isinstance(value, (list, tuple)):
        return json.dumps([str(item).strip() for item in value], separators=(",", ":"))
    if isinstance(value, dict):
        return json.dumps({str(k): str(v).strip() for k, v in sorted(value.items())},
                          separators=(",", ":"))
    return json.dumps(str(value).strip(), separators=(",", ":"))


def value_hash(value: Any) -> str:
    return hashlib.sha256(canonical_value(value).encode("utf-8")).hexdigest()


@dataclass
class Approval:
    approval_id: str
    decision_id: str
    report_id: str
    report_version: int
    approved_value: Any
    value_hash: str
    human_identity: str
    approved_at: str
    approval_method: str
    evidence_reference: str
    supersedes: str | None = None
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


def validate(approval: Approval) -> list[str]:
    """Every reason this approval must not be accepted. Empty means valid."""
    problems: list[str] = []

    if not approval.approval_id.startswith("APR-"):
        problems.append("approval_id must start with 'APR-'")
    if not approval.decision_id.strip():
        problems.append("decision_id is empty")
    if approval.approval_method not in VALID_METHODS:
        problems.append(
            f"approval_method {approval.approval_method!r} is not a recognised "
            f"human action; valid: {sorted(VALID_METHODS)}")

    identity = approval.human_identity.strip()
    if not identity:
        problems.append("human_identity is empty — an approval needs a named person")
    elif FORBIDDEN_IDENTITY.search(identity):
        problems.append(
            f"human_identity {identity!r} looks like an automated actor. An agent "
            f"may propose but may never approve (Part 41.3).")

    if approval.approved_value == SENTINEL:
        problems.append("cannot approve the PENDING_APPROVAL sentinel itself")
    if approval.value_hash != value_hash(approval.approved_value):
        problems.append(
            "value_hash does not match approved_value — the record has been "
            "altered since it was created")
    if not approval.evidence_reference.strip():
        problems.append("evidence_reference is empty")
    if not approval.approved_at.strip():
        problems.append("approved_at is empty")
    return problems


def store_path(report_id: str, root: Path | None = None) -> Path:
    return (root or APPROVALS_DIR) / f"{report_id}.approvals.jsonl"


def record(approval: Approval, *, root: Path | None = None) -> Approval:
    """Append a validated approval. Refuses anything that fails validation."""
    problems = validate(approval)
    if problems:
        raise ApprovalError("; ".join(problems))

    path = store_path(approval.report_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(approval.to_json() + "\n")
    return approval


def load(report_id: str, *, root: Path | None = None) -> list[Approval]:
    path = store_path(report_id, root)
    if not path.exists():
        return []
    approvals: list[Approval] = []
    for line in path.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        payload.setdefault("extra", {})
        approvals.append(Approval(**payload))
    return approvals


def effective(report_id: str, *, root: Path | None = None) -> dict[str, Approval]:
    """The currently binding approval per decision, superseded ones removed."""
    result: dict[str, Approval] = {}
    superseded: set[str] = set()
    for approval in load(report_id, root=root):
        if approval.supersedes:
            superseded.add(approval.supersedes)
        result[approval.decision_id] = approval
    return {decision: approval for decision, approval in result.items()
            if approval.approval_id not in superseded}


@dataclass(frozen=True)
class DecisionStatus:
    decision_id: str
    state: str          # CONFIRMED | NEEDS_YOUR_APPROVAL | UNKNOWN
    detail: str
    approved_by: str = ""


def status_for(
    report_id: str,
    decisions: dict[str, Any],
    *,
    root: Path | None = None,
    mode: str = "prototype",
) -> list[DecisionStatus]:
    """Compare current configuration values against binding approvals.

    This is the check that makes the value binding real: an approval only
    counts while the configuration still holds the value that was approved.
    """
    binding = effective(report_id, root=root)
    statuses: list[DecisionStatus] = []

    for decision_id, current in sorted(decisions.items()):
        approval = binding.get(decision_id)
        if current == SENTINEL or current is None:
            statuses.append(DecisionStatus(
                decision_id, "UNKNOWN",
                "No value yet. A named human must decide this."))
            continue
        if approval is None:
            statuses.append(DecisionStatus(
                decision_id, "NEEDS_YOUR_APPROVAL",
                f"Proposed value is set but nobody has approved it: {current!r}"))
            continue
        if approval.value_hash != value_hash(current):
            statuses.append(DecisionStatus(
                decision_id, "NEEDS_YOUR_APPROVAL",
                f"The value changed after approval. Approved "
                f"{approval.approved_value!r}, now {current!r}.",
                approval.human_identity))
            continue
        if approval.approval_method == "fixture" and mode == "production":
            statuses.append(DecisionStatus(
                decision_id, "NEEDS_YOUR_APPROVAL",
                "Approved as fixture test data, which is not valid in production "
                "(Part 41.4).", approval.human_identity))
            continue
        statuses.append(DecisionStatus(
            decision_id, "CONFIRMED",
            f"Approved via {approval.approval_method} on {approval.approved_at}.",
            approval.human_identity))
    return statuses


def new_approval_id(decision_id: str, report_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    digest = hashlib.sha256(f"{report_id}:{decision_id}:{stamp}".encode()).hexdigest()[:8]
    return f"APR-{stamp}-{digest}"


def propose(decision_id: str, value: Any, rationale: str) -> dict[str, Any]:
    """What an agent produces instead of an approval.

    Always labelled, never binding. This is the correct way for an agent to be
    helpful about a human-owned decision (Part 41.3).
    """
    return {
        "decision_id": decision_id,
        "suggested_value": value,
        "rationale": rationale,
        "status": "SUGGESTED — HUMAN APPROVAL REQUIRED",
        "binding": False,
    }


# -- keeping report.toml in sync ---------------------------------------

_APPROVAL_LINE = re.compile(
    r'^(?P<key>[a-z_][a-z0-9_]*)\s*=\s*\{\s*approved_by\s*=\s*"[^"]*"\s*,\s*'
    r'approved_at\s*=\s*"[^"]*"\s*,\s*evidence\s*=\s*"[^"]*"\s*\}\s*$')


def sync_report_toml(report_id: str, *, reports_root: Path | None = None,
                     approvals_root: Path | None = None) -> list[str]:
    """Project the Factory's approval store onto `report.toml`'s `[approvals]`
    block, so the one file `PROJECT_TOOL report validate` reads reflects what
    was actually approved.

    `factory/approvals/<id>.approvals.jsonl` is the source of truth — it alone
    carries hash binding, identity and evidence. The block written here is a
    GENERATED PROJECTION of it, the same relationship `.ai/PROJECT_MAP.md`'s
    generated catalog has to the file tree (Part 21: one source per concept).
    Only decisions whose value_hash still matches the current configuration
    are synced as approved; anything else stays blank and `report validate`
    correctly reports it as unapproved.

    Returns the decision ids that were written as approved.
    """
    import tomllib

    reports_root = reports_root or (Path(__file__).resolve().parent.parent / "reports")
    config_path = reports_root / report_id / "report.toml"
    if not config_path.exists():
        return []

    text = config_path.read_text("utf-8")
    config = tomllib.loads(text)
    binding = effective(report_id, root=approvals_root)

    # What value does each decision currently hold, so we only project an
    # approval that still matches (the same rule status_for() applies).
    history = config.get("history", {})
    quality = config.get("quality", {})
    output = config.get("output", {})
    current_values = {
        "business_key": history.get("business_key"),
        "load_mode": config.get("load_mode"),
        "deletion_rule": history.get("deletion_rule"),
        "control_total_column": quality.get("control_total_column"),
        "storage_allowed": output.get("storage_allowed"),
    }

    lines = text.splitlines()
    in_approvals = False
    synced: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "[approvals]":
            in_approvals = True
            continue
        if in_approvals and stripped.startswith("["):
            in_approvals = False
        if not in_approvals:
            continue
        match = _APPROVAL_LINE.match(stripped)
        if not match:
            continue
        key = match.group("key")
        approval = binding.get(key)
        current = current_values.get(key)
        if (approval is not None and current is not None
                and approval.value_hash == value_hash(current)):
            lines[index] = (
                f'{key} = {{ approved_by = "{approval.human_identity}", '
                f'approved_at = "{approval.approved_at}", '
                f'evidence = "{approval.evidence_reference}" }}')
            synced.append(key)
        else:
            lines[index] = (
                f'{key} = {{ approved_by = "", approved_at = "", evidence = "" }}')

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return synced
