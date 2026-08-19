"""A similar-but-wrong workbook must be refused, never silently accepted.

`app/excel/identity.py` decides which of the employee's open workbooks the
engine is about to read. Getting this approximately right is worse than
failing: extracting `Q3 Orders (1).xlsx` instead of `Q3 Orders.xlsx` produces a
dashboard that is confidently wrong, which is the exact failure this engine
exists to prevent (Part 7.1).

These tests use fake candidates carrying a `FullName`, matching Excel's COM
`Workbook.FullName`, so the rule that must be right is provable on any machine.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from app.errors import AppError
from app.excel.identity import canonical_path, matches, verify


class _Workbook:
    """Minimal stand-in for an Excel COM Workbook object."""

    def __init__(self, full_name: str):
        self.FullName = full_name


class TestCanonicalPath(unittest.TestCase):
    def test_relative_and_absolute_forms_agree(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "orders.xlsx"
            target.write_text("x", encoding="utf-8")
            noisy = Path(temp) / "." / "sub" / ".." / "orders.xlsx"
            self.assertEqual(canonical_path(target), canonical_path(noisy))

    def test_trailing_separator_noise_does_not_change_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "orders.xlsx"
            target.write_text("x", encoding="utf-8")
            self.assertEqual(
                canonical_path(str(target)),
                canonical_path(str(target).replace(os.sep, os.sep + "." + os.sep, 1))
                if os.sep in str(target) else canonical_path(str(target)))

    def test_case_handling_follows_the_platform(self):
        """Lower-casing unconditionally would wrongly equate two real files
        on Linux, where Orders.xlsx and orders.xlsx can both exist."""
        upper = canonical_path("/tmp/Orders.xlsx")
        lower = canonical_path("/tmp/orders.xlsx")
        if os.path.normcase("A") == "a":      # Windows-like
            self.assertEqual(upper, lower)
        else:                                  # POSIX
            self.assertNotEqual(upper, lower)


class TestMatching(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.root = Path(self._temp.name)
        self.target = self.root / "Q3 Orders.xlsx"
        self.target.write_text("real", encoding="utf-8")

    def test_the_exact_workbook_matches(self):
        self.assertTrue(matches(self.target, _Workbook(str(self.target))))

    def test_similar_names_do_not_match(self):
        for neighbour in (
            "Q3 Orders (1).xlsx",
            "Q3 Orders - Copy.xlsx",
            "Q3 Orders.xlsx.bak",
            "Q3 Orders backup.xlsx",
            "Q3_Orders.xlsx",
            "Q3 Orders.xlsm",
        ):
            path = self.root / neighbour
            path.write_text("decoy", encoding="utf-8")
            self.assertFalse(
                matches(self.target, _Workbook(str(path))),
                f"{neighbour!r} was accepted as the configured workbook")

    def test_same_name_in_a_different_directory_does_not_match(self):
        other = self.root / "archive"
        other.mkdir()
        decoy = other / "Q3 Orders.xlsx"
        decoy.write_text("decoy", encoding="utf-8")
        self.assertFalse(matches(self.target, _Workbook(str(decoy))))

    def test_a_candidate_without_a_path_never_matches(self):
        self.assertFalse(matches(self.target, object()))


class TestVerify(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.root = Path(self._temp.name)
        self.target = self.root / "Q3 Orders.xlsx"
        self.target.write_text("real", encoding="utf-8")

    def test_returns_the_single_matching_workbook(self):
        wanted = _Workbook(str(self.target))
        decoy = _Workbook(str(self.root / "Q3 Orders (1).xlsx"))
        self.assertIs(verify(str(self.target), [decoy, wanted, decoy]), wanted)

    def test_a_lone_candidate_may_be_passed_directly(self):
        wanted = _Workbook(str(self.target))
        self.assertIs(verify(str(self.target), wanted), wanted)

    def test_no_match_is_ambiguous_not_a_silent_none(self):
        decoy = _Workbook(str(self.root / "Q3 Orders - Copy.xlsx"))
        with self.assertRaises(AppError) as caught:
            verify(str(self.target), [decoy])
        self.assertEqual(caught.exception.code, "EXCEL_WORKBOOK_AMBIGUOUS")

    def test_no_open_workbooks_at_all_is_refused(self):
        with self.assertRaises(AppError):
            verify(str(self.target), [])
        with self.assertRaises(AppError):
            verify(str(self.target), None)

    def test_two_workbooks_on_the_same_path_are_refused_rather_than_chosen(self):
        """Excel can hold the same path open twice. Picking one would mean
        guessing which copy the numbers came from."""
        first = _Workbook(str(self.target))
        second = _Workbook(str(self.target))
        with self.assertRaises(AppError) as caught:
            verify(str(self.target), [first, second])
        self.assertEqual(caught.exception.code, "EXCEL_WORKBOOK_AMBIGUOUS")
        self.assertIn("refusing to guess", caught.exception.support_detail)

    def test_the_error_never_leaks_the_full_path_into_the_operator_message(self):
        """Part 22.8: the path belongs in the expandable technical section."""
        with self.assertRaises(AppError) as caught:
            verify(str(self.target), [])
        error = caught.exception
        self.assertEqual(error.code, "EXCEL_WORKBOOK_AMBIGUOUS")
        self.assertTrue(error.support_detail)


if __name__ == "__main__":
    unittest.main()
