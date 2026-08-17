"""Error registry (Constitution Parts 12.3, 12.4, 22.8, 42.2).

Application code raises codes from `contracts/error_codes.json` only. A literal
error string that is not in the registry fails the architecture verifier.

This is what makes Part 22.8's four-part operator error screen a build-time
guarantee rather than a design aspiration: the screen is assembled from these
fields, so an error can never reach the employee as a raw stack trace.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "error_codes.json"

RETRYABLE = "RETRYABLE"
USER_ACTION = "USER_ACTION"
BLOCKING_DATA = "BLOCKING_DATA"
BLOCKING_SYSTEM = "BLOCKING_SYSTEM"

VALID_CLASSES = frozenset({RETRYABLE, USER_ACTION, BLOCKING_DATA, BLOCKING_SYSTEM})


@dataclass(frozen=True)
class ErrorDefinition:
    code: str
    error_class: str
    retryable: bool
    part: str
    operator_message_en: str
    operator_message_ar: str
    next_action: str
    preserves_history: bool


@lru_cache(maxsize=1)
def registry(path: Path | None = None) -> dict[str, ErrorDefinition]:
    data = json.loads((path or CONTRACT_PATH).read_text(encoding="utf-8"))
    result: dict[str, ErrorDefinition] = {}
    for entry in data["codes"]:
        result[entry["code"]] = ErrorDefinition(
            code=entry["code"],
            error_class=entry["class"],
            retryable=bool(entry["retryable"]),
            part=entry.get("part", ""),
            operator_message_en=entry["operator_message_en"],
            operator_message_ar=entry["operator_message_ar"],
            next_action=entry["next_action"],
            preserves_history=bool(entry.get("preserves_history", True)),
        )
    return result


class AppError(Exception):
    """Every failure the operator can see. Carries a registry code, never prose.

    `support_detail` is for the expandable technical section only. It must never
    become the primary message the employee reads (Part 22.8).
    """

    def __init__(self, code: str, support_detail: str = "", **context: object) -> None:
        definition = registry().get(code)
        if definition is None:
            raise KeyError(
                f"{code!r} is not in contracts/error_codes.json. Add it there "
                f"with an operator message and next action (Part 42.2) — do not "
                f"raise an unregistered error string.")
        self.definition = definition
        self.code = code
        self.support_detail = support_detail
        self.context = context
        super().__init__(f"{code}: {definition.operator_message_en}")

    @property
    def retryable(self) -> bool:
        return self.definition.retryable

    @property
    def preserves_history(self) -> bool:
        return self.definition.preserves_history

    def operator_screen(self, language: str = "en") -> dict[str, object]:
        """The four-part non-technical error screen (Part 22.8)."""
        message = (self.definition.operator_message_ar if language == "ar"
                   else self.definition.operator_message_en)
        return {
            "what_went_wrong": message,
            "is_my_data_safe": self.definition.preserves_history,
            "next_action": self.definition.next_action,
            "support_code": self.code,
            "support_detail": self.support_detail,
        }
