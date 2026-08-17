"""Error registry (Constitution Parts 12.3, 22.8, 42.2)."""

from __future__ import annotations

import unittest

from app.errors import VALID_CLASSES, AppError, registry


class TestErrorRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = registry()

    def test_registry_is_not_empty(self):
        self.assertGreater(len(self.registry), 20)

    def test_every_code_has_a_valid_class(self):
        for code, definition in self.registry.items():
            self.assertIn(definition.error_class, VALID_CLASSES,
                          f"{code} has an invalid class")

    def test_every_code_has_both_operator_languages(self):
        # Part 22.9: Arabic and English share one data contract.
        for code, definition in self.registry.items():
            self.assertTrue(definition.operator_message_en.strip(), f"{code}: no English message")
            self.assertTrue(definition.operator_message_ar.strip(), f"{code}: no Arabic message")

    def test_every_code_names_a_next_action(self):
        # Part 22.8: the operator always gets ONE next action.
        for code, definition in self.registry.items():
            self.assertTrue(definition.next_action.strip(), f"{code}: no next action")

    def test_operator_messages_contain_no_developer_jargon(self):
        # Part 22.8: never expose a raw stack trace as the primary message.
        jargon = ("traceback", "exception", "null pointer", "stack trace",
                  "errno", "0x", "at line")
        for code, definition in self.registry.items():
            lowered = definition.operator_message_en.lower()
            for term in jargon:
                self.assertNotIn(term, lowered, f"{code} leaks jargon: {term}")

    def test_data_errors_preserve_history(self):
        # Rule 9 / Part 12.6: a failure never corrupts trusted history, and the
        # operator must be told their previous dashboard is still correct.
        for code, definition in self.registry.items():
            if definition.error_class in ("BLOCKING_DATA", "BLOCKING_SYSTEM"):
                self.assertTrue(definition.preserves_history,
                                f"{code} claims to damage trusted history")

    def test_retryable_flag_matches_class(self):
        for code, definition in self.registry.items():
            if definition.error_class == "BLOCKING_DATA":
                self.assertFalse(
                    definition.retryable,
                    f"{code}: a real data problem must not be retried (Part 12.4)")

    def test_control_total_mismatch_is_never_retryable(self):
        # Part 12.4 names this explicitly under "never retry".
        self.assertFalse(self.registry["DQ_CONTROL_TOTAL_MISMATCH"].retryable)

    def test_required_column_missing_is_never_retryable(self):
        self.assertFalse(self.registry["SCHEMA_REQUIRED_COLUMN_MISSING"].retryable)


class TestAppError(unittest.TestCase):
    def test_unregistered_code_is_refused(self):
        # Part 42.2: code raises registry codes only, never an ad-hoc string.
        with self.assertRaises(KeyError) as caught:
            AppError("SOMETHING_I_JUST_INVENTED")
        self.assertIn("error_codes.json", str(caught.exception))

    def test_operator_screen_has_all_four_parts(self):
        error = AppError("DQ_CONTROL_TOTAL_MISMATCH", support_detail="delta=17")
        screen = error.operator_screen()
        self.assertIn("what_went_wrong", screen)
        self.assertIn("is_my_data_safe", screen)
        self.assertIn("next_action", screen)
        self.assertIn("support_code", screen)
        self.assertTrue(screen["is_my_data_safe"])
        self.assertEqual(screen["support_code"], "DQ_CONTROL_TOTAL_MISMATCH")

    def test_operator_screen_switches_language(self):
        error = AppError("DRM_USER_ACTION_REQUIRED")
        self.assertNotEqual(
            error.operator_screen("en")["what_went_wrong"],
            error.operator_screen("ar")["what_went_wrong"],
        )

    def test_support_detail_is_separate_from_the_message(self):
        error = AppError("EXCEL_OPEN_FAILED", support_detail="COM 0x800A03EC")
        screen = error.operator_screen()
        self.assertNotIn("0x800A03EC", screen["what_went_wrong"])
        self.assertEqual(screen["support_detail"], "COM 0x800A03EC")


if __name__ == "__main__":
    unittest.main()
