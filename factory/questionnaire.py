"""The business interview (Constitution Parts 3.1, 4, 41).

A non-technical employee must never be asked to fill in a technical table. The
translation from human answers to technical contract is the Factory's job.

The rule for every question here: **ask about the business, never about the
implementation.**

    Bad:  What is the grain?
    Good: What does one row in your Excel file represent?

    Bad:  Select load mode: append / upsert / snapshot / replace_period.
    Good: Can records from earlier days be corrected later?

Progressive disclosure: the ten questions in `CORE_QUESTIONS` are what an
ordinary employee sees. Advanced concepts appear only when an answer makes them
relevant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Decisions Part 3.1 reserves to a named human. The Factory may collect and
#: translate these; it may never decide them.
HUMAN_OWNED = (
    "purpose", "grain", "business_key", "control_total_column", "load_mode",
    "lookback_days", "deletion_rule", "storage_allowed", "business_owner",
    "dashboard_decision",
)


@dataclass
class Choice:
    value: str
    label: str
    help_text: str = ""


@dataclass
class Question:
    id: str
    prompt: str
    why: str
    examples: tuple[str, ...] = ()
    choices: tuple[Choice, ...] = ()
    kind: str = "text"            # text | choice | multi | files | people
    advanced: bool = False
    depends_on: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "prompt": self.prompt, "why": self.why,
            "examples": list(self.examples), "kind": self.kind,
            "advanced": self.advanced, "depends_on": self.depends_on,
            "choices": [{"value": c.value, "label": c.label, "help": c.help_text}
                        for c in self.choices],
        }


CORE_QUESTIONS: tuple[Question, ...] = (
    Question(
        id="purpose",
        prompt="What are you trying to automate?",
        why="It becomes the report's name and tells everyone what this is for.",
        examples=("The weekly production quality report I build every Monday",
                  "The daily output summary I send to the plant manager"),
    ),
    Question(
        id="sources",
        prompt="Add the Excel files you use for this report.",
        why="We look at their structure — never their contents — to suggest column "
            "names for you to confirm.",
        kind="files",
    ),
    Question(
        id="grain",
        prompt="What does ONE ROW in your file represent?",
        why="This is the single most important answer. Everything else depends on "
            "it, and nobody but you can answer it.",
        examples=("One production order, for one model, on one line, on one date",
                  "One invoice line",
                  "One machine reading at one timestamp"),
    ),
    Question(
        id="control_total_column",
        prompt="Which number do you already use to check that the report is correct?",
        why="We compare it between your file and the system after every run. If they "
            "ever differ, we stop and tell you instead of showing a wrong number.",
        examples=("Total produced quantity", "Total invoice amount", "Total headcount"),
    ),
    Question(
        id="corrections",
        prompt="Can records from earlier days or weeks be corrected later?",
        why="It decides whether a new file adds to your history or also fixes it.",
        kind="choice",
        choices=(
            Choice("only_new",
                   "No — each file only contains brand-new records",
                   "Nothing already recorded ever changes."),
            Choice("can_be_corrected",
                   "Yes — earlier records are sometimes corrected",
                   "A later file may contain a fixed version of an earlier record."),
            Choice("full_picture",
                   "Each file contains the complete current picture",
                   "The newest file replaces your whole view, not just new rows."),
            Choice("replaces_period",
                   "Each file completely replaces one period",
                   "For example, the new March file replaces all of March."),
        ),
    ),
    Question(
        id="correction_window",
        prompt="How many days back do corrections usually happen?",
        why="We re-check that window on every run and treat anything older as final.",
        examples=("7", "14", "30"),
        depends_on="corrections=can_be_corrected",
    ),
    Question(
        id="disappearing_rows",
        prompt="If a record stops appearing in new files, what does that mean?",
        why="We must be told. Guessing that a missing row means 'deleted' can quietly "
            "erase real history.",
        kind="choice",
        choices=(
            Choice("ignore", "Nothing — old records just stop being sent",
                   "Keep the record exactly as it is."),
            Choice("mark_inactive", "It is no longer active",
                   "Keep it, but mark it inactive so it leaves current totals."),
            Choice("soft_delete", "It was cancelled or withdrawn",
                   "Keep it for audit, exclude it from reporting."),
        ),
    ),
    Question(
        id="dashboard_decision",
        prompt="What decision should the dashboard help you make?",
        why="A chart that supports no decision gets removed. This keeps the page "
            "about your work rather than about the data.",
        examples=("Where production loss is concentrated this week",
                  "Which supplier to raise a quality claim against",
                  "Whether we will hit this month's target"),
    ),
    Question(
        id="business_owner",
        prompt="Who owns and approves this report?",
        why="Business meaning needs a named person. That person approves what the "
            "numbers mean — not how the software works.",
        examples=("Production Control — Sara Ahmed", "Quality Manager — Omar Hassan"),
        kind="people",
    ),
    Question(
        id="storage_allowed",
        prompt="Where may the extracted data be stored?",
        why="Once extracted, the data no longer carries your file's protection. IT "
            "must approve where it lives.",
        examples=("D:/secure/production-reports", "The approved department folder"),
    ),
)

ADVANCED_QUESTIONS: tuple[Question, ...] = (
    Question(
        id="business_key_columns",
        prompt="Which columns together identify one record?",
        why="Two rows with the same values here are the same record. It is how we "
            "recognise a correction instead of creating a duplicate.",
        examples=("Date + Production Line + Order Number + Model",),
        kind="multi",
        advanced=True,
    ),
    Question(
        id="approved_categories",
        prompt="Which values are valid for your main category column?",
        why="Anything outside the list is loaded but flagged, so a new category is "
            "noticed rather than silently absorbed.",
        kind="multi",
        advanced=True,
    ),
)


# -- translation -----------------------------------------------------------

#: Plain answers -> the technical load mode. This mapping is the entire reason
#: the employee never has to learn the words "upsert" or "snapshot".
LOAD_MODE_BY_ANSWER = {
    "only_new": "append",
    "can_be_corrected": "upsert",
    "full_picture": "snapshot",
    "replaces_period": "replace_period",
}

LOAD_MODE_EXPLANATION = {
    "append": "Each new file adds records. Nothing already recorded changes.",
    "upsert": "New files add records and update ones that were corrected.",
    "snapshot": "Each file is the complete current picture at that point in time.",
    "replace_period": "Each file completely replaces one approved period.",
}


@dataclass
class Interview:
    """One employee's answers, plus what the Factory derived from them."""

    report_id: str
    answers: dict[str, Any] = field(default_factory=dict)

    def answer(self, question_id: str, value: Any) -> None:
        self.answers[question_id] = value

    @property
    def unanswered_core(self) -> list[str]:
        return [
            question.id for question in CORE_QUESTIONS
            if question.id not in self.answers
            and not self._skipped(question)
        ]

    def _skipped(self, question: Question) -> bool:
        if not question.depends_on:
            return False
        key, _, expected = question.depends_on.partition("=")
        return self.answers.get(key) != expected

    def visible_questions(self) -> list[Question]:
        """Progressive disclosure: only what this employee actually needs."""
        return [q for q in CORE_QUESTIONS if not self._skipped(q)]

    # -- derivation ---------------------------------------------------------

    def load_mode(self) -> str:
        answer = self.answers.get("corrections")
        return LOAD_MODE_BY_ANSWER.get(answer, "PENDING_APPROVAL")

    def lookback_days(self) -> Any:
        if self.answers.get("corrections") != "can_be_corrected":
            return 0
        raw = self.answers.get("correction_window")
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            return "PENDING_APPROVAL"

    def deletion_rule(self) -> str:
        return self.answers.get("disappearing_rows", "PENDING_APPROVAL")

    def technical_contract(self) -> dict[str, Any]:
        """The technical values derived from plain answers.

        Everything unanswered stays `PENDING_APPROVAL` — the Factory translates,
        it never invents (Part 41.3).
        """
        return {
            "load_mode": self.load_mode(),
            "lookback_days": self.lookback_days(),
            "deletion_rule": self.deletion_rule(),
            "business_key": self.answers.get("business_key_columns", "PENDING_APPROVAL"),
            "control_total_column": self.answers.get(
                "control_total_column", "PENDING_APPROVAL"),
            "storage_allowed": self.answers.get("storage_allowed", "PENDING_APPROVAL"),
            "grain": self.answers.get("grain", "PENDING_APPROVAL"),
            "purpose": self.answers.get("purpose", "PENDING_APPROVAL"),
            "dashboard_decision": self.answers.get(
                "dashboard_decision", "PENDING_APPROVAL"),
            "business_owner": self.answers.get("business_owner", "PENDING_APPROVAL"),
        }

    def understanding_review(self) -> list[dict[str, str]]:
        """The plain-language summary shown before any code is written.

        The employee approves MEANING here, not implementation (brief §7).
        """
        contract = self.technical_contract()
        rows = [
            ("One record", contract["grain"],
             "What one row in your file represents"),
            ("New files", LOAD_MODE_EXPLANATION.get(
                contract["load_mode"], "Not yet decided"),
             "How new files join your existing history"),
            ("Unique record", _describe_list(contract["business_key"]),
             "The columns that identify one record"),
            ("Main accuracy check", contract["control_total_column"],
             "The number we compare between your file and the system"),
            ("Dashboard decision", contract["dashboard_decision"],
             "The decision this dashboard supports"),
            ("Missing records", _describe_deletion(contract["deletion_rule"]),
             "What it means when a record stops appearing"),
            ("Data storage", _describe_list(contract["storage_allowed"]),
             "Where the extracted data may live"),
            ("Approved by", contract["business_owner"],
             "Who owns the meaning of this report"),
        ]
        return [
            {"item": item, "understanding": str(value), "explanation": explanation}
            for item, value, explanation in rows
        ]


def _describe_list(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return " + ".join(str(item) for item in value) if value else "PENDING_APPROVAL"
    return str(value)


def _describe_deletion(rule: str) -> str:
    return {
        "ignore": "Keep the record unchanged.",
        "mark_inactive": "Keep it, but mark it inactive.",
        "soft_delete": "Keep it for audit, exclude it from reporting.",
    }.get(rule, "PENDING_APPROVAL")
