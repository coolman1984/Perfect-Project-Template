"""Run state machine (Constitution Parts 12.2, 25.6, 42.3).

Part 42.3 requires proof that every state is reachable, terminal states have no
outgoing edges, and no transition exists that Part 25.6 does not permit.
"""

from __future__ import annotations

import unittest

from app.state_machine import IllegalTransition, RunStateMachine, load_contract


class TestStateContract(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    def test_initial_state_is_created(self):
        self.assertEqual(self.contract.initial_state, "CREATED")

    def test_terminal_states_have_no_outgoing_transitions(self):
        for state in self.contract.terminal_states:
            self.assertEqual(
                self.contract.transitions[state], frozenset(),
                f"{state} is terminal but has outgoing transitions (Part 25.6)")

    def test_every_transition_target_is_a_declared_state(self):
        for source, targets in self.contract.transitions.items():
            for target in targets:
                self.assertIn(target, self.contract.states,
                              f"{source} -> {target} names an undeclared state")

    def test_every_state_is_reachable_from_the_initial_state(self):
        reachable = {self.contract.initial_state}
        frontier = [self.contract.initial_state]
        while frontier:
            for target in self.contract.transitions[frontier.pop()]:
                if target not in reachable:
                    reachable.add(target)
                    frontier.append(target)
        unreachable = self.contract.states - reachable
        self.assertEqual(unreachable, frozenset(),
                         f"unreachable states: {sorted(unreachable)}")

    def test_every_non_terminal_state_can_fail(self):
        # Rule 9: a failure must never corrupt trusted history, which means
        # every working state needs a defined way to fail safely.
        for state, targets in self.contract.transitions.items():
            if state in self.contract.terminal_states:
                continue
            self.assertIn("FAILED", targets, f"{state} has no path to FAILED")


class TestRunStateMachine(unittest.TestCase):
    def test_happy_path_reaches_complete(self):
        machine = RunStateMachine()
        for state in ("CHECKING_SOURCE", "OPENING_EXCEL", "EXTRACTING", "STAGING",
                      "VALIDATING", "CLEANING", "UPDATING_HISTORY", "ARCHIVING",
                      "CALCULATING", "BUILDING_INSIGHTS", "BUILDING_JSON",
                      "BUILDING_DASHBOARD", "VERIFYING", "COMPLETE"):
            machine.to(state)
        self.assertEqual(machine.state, "COMPLETE")
        self.assertTrue(machine.is_terminal)

    def test_illegal_transition_is_rejected(self):
        machine = RunStateMachine()
        # Skipping the quality gate is exactly what Part 9 forbids.
        with self.assertRaises(IllegalTransition):
            machine.to("UPDATING_HISTORY")

    def test_unknown_state_is_rejected(self):
        machine = RunStateMachine()
        with self.assertRaises(IllegalTransition) as caught:
            machine.to("DEFINITELY_NOT_A_STATE")
        self.assertIn("run_states.json", str(caught.exception))

    def test_terminal_state_cannot_transition(self):
        machine = RunStateMachine()
        machine.to("CANCELLED")
        with self.assertRaises(IllegalTransition):
            machine.to("CHECKING_SOURCE")

    def test_history_is_preserved(self):
        # Part 25.6: a retry does not erase the previous event record.
        machine = RunStateMachine()
        machine.to("CHECKING_SOURCE")
        machine.to("WAITING_FOR_FILE")
        machine.to("CHECKING_SOURCE")
        self.assertEqual(
            machine.history,
            ("CREATED", "CHECKING_SOURCE", "WAITING_FOR_FILE", "CHECKING_SOURCE"))

    def test_waiting_for_user_preserves_the_run(self):
        # Part 22.5: a required user action is not a technical failure.
        machine = RunStateMachine()
        machine.to("CHECKING_SOURCE")
        machine.to("OPENING_EXCEL")
        machine.to("WAITING_FOR_USER")
        self.assertTrue(machine.can("EXTRACTING"))
        self.assertFalse(machine.is_terminal)


if __name__ == "__main__":
    unittest.main()
