"""Run state machine (Constitution Parts 12.2, 25.6, 42.3).

Transitions are loaded from `contracts/run_states.json` rather than hard-coded,
so adding a state is a contract change with a version bump (Part 25.7) instead
of a quiet edit in Python.

This module is deliberately complete: it is pure logic with no environment
dependency, so it works and is tested from day one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "run_states.json"


class IllegalTransition(RuntimeError):
    """An attempt to move the run somewhere Part 25.6 does not permit."""


@dataclass(frozen=True)
class StateContract:
    initial_state: str
    terminal_states: frozenset[str]
    transitions: dict[str, frozenset[str]]
    descriptions: dict[str, str] = field(default_factory=dict)

    @property
    def states(self) -> frozenset[str]:
        return frozenset(self.transitions)


def load_contract(path: Path | None = None) -> StateContract:
    data = json.loads((path or CONTRACT_PATH).read_text(encoding="utf-8"))
    states = data["states"]
    return StateContract(
        initial_state=data["initial_state"],
        terminal_states=frozenset(data["terminal_states"]),
        transitions={name: frozenset(body.get("to", [])) for name, body in states.items()},
        descriptions={name: body.get("description", "") for name, body in states.items()},
    )


class RunStateMachine:
    """Validates every transition and records the full history.

    A retry creates a linked attempt or resumes from a verified checkpoint; it
    never erases the previous event record (Part 25.6).
    """

    def __init__(self, contract: StateContract | None = None) -> None:
        self._contract = contract or load_contract()
        self._state = self._contract.initial_state
        self._history: list[str] = [self._state]

    @property
    def state(self) -> str:
        return self._state

    @property
    def history(self) -> tuple[str, ...]:
        return tuple(self._history)

    @property
    def is_terminal(self) -> bool:
        return self._state in self._contract.terminal_states

    def can(self, target: str) -> bool:
        return target in self._contract.transitions.get(self._state, frozenset())

    def to(self, target: str) -> str:
        if target not in self._contract.states:
            raise IllegalTransition(
                f"unknown state {target!r}. Add it to contracts/run_states.json "
                f"as a versioned contract change (Part 42.3).")
        if self.is_terminal:
            raise IllegalTransition(
                f"{self._state} is terminal; it has no outgoing transitions "
                f"(Part 25.6). Start a new linked attempt instead.")
        if not self.can(target):
            legal = ", ".join(sorted(self._contract.transitions[self._state])) or "(none)"
            raise IllegalTransition(
                f"illegal transition {self._state} -> {target}. Legal: {legal}")
        self._state = target
        self._history.append(target)
        return self._state
