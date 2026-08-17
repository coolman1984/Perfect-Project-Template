"""Value conversion and column normalization (Constitution Parts 7.4, 7.6).

These rules must be deterministic: the same input produces the same output,
always. That is what lets reconciliation land on exactly zero (Part 9.4).
"""

from __future__ import annotations

import unittest
from decimal import Decimal

from app.excel.conversion import (
    excel_serial_to_date, is_blank, is_excel_error, normalize_column_name,
    normalize_header, to_decimal,
)


class TestColumnNormalization(unittest.TestCase):
    """Part 7.6 — the seven deterministic rules."""

    def test_documented_example(self):
        self.assertEqual(normalize_column_name("  Total Cost (USD) "), "total_cost_usd")

    def test_trims_lowercases_and_collapses_separators(self):
        self.assertEqual(normalize_column_name("Order   Number"), "order_number")
        self.assertEqual(normalize_column_name("Defect%Rate"), "defect_rate")
        self.assertEqual(normalize_column_name("--Line--"), "line")

    def test_leading_digit_is_prefixed(self):
        self.assertEqual(normalize_column_name("2026 Total"), "c_2026_total")

    def test_empty_name_uses_position(self):
        self.assertEqual(normalize_column_name("   ", position=4), "col_4")
        self.assertEqual(normalize_column_name("!!!", position=7), "col_7")

    def test_is_deterministic(self):
        raw = " Manuf. Part # "
        self.assertEqual(normalize_column_name(raw), normalize_column_name(raw))

    def test_duplicate_headers_get_deterministic_suffixes(self):
        # Part 27.3: the mapping must then choose the intended one explicitly.
        self.assertEqual(
            normalize_header(["Manuf. Part", "Log File", "Manuf. Part", "Manuf. Part"]),
            ["manuf_part", "log_file", "manuf_part_2", "manuf_part_3"],
        )

    def test_header_normalization_handles_blanks_by_position(self):
        self.assertEqual(normalize_header(["Qty", "", "Line"]), ["qty", "col_1", "line"])


class TestBlankAndErrorDetection(unittest.TestCase):
    def test_blank_and_whitespace_only_are_null(self):
        for value in (None, "", "   ", "\t\n"):
            self.assertTrue(is_blank(value), f"{value!r} should be blank")

    def test_zero_is_not_blank(self):
        # A real zero is data. Treating it as blank would silently lose rows.
        self.assertFalse(is_blank(0))

    def test_excel_errors_are_detected_not_zeroed(self):
        for value in ("#N/A", "#VALUE!", "#DIV/0!", "#REF!", "#NAME?"):
            self.assertTrue(is_excel_error(value))
        # Part 7.4: count them, never silently convert them to zero.
        self.assertIsNone(to_decimal("#DIV/0!"))


class TestDecimalConversion(unittest.TestCase):
    """Part 7.4 — money is DECIMAL, never floating point."""

    def test_plain_numbers(self):
        self.assertEqual(to_decimal(1234), Decimal("1234"))
        self.assertEqual(to_decimal("1234.56"), Decimal("1234.56"))

    def test_thousands_separators_are_stripped(self):
        self.assertEqual(to_decimal("1,234,567.89"), Decimal("1234567.89"))

    def test_accounting_negatives(self):
        self.assertEqual(to_decimal("(1,234.50)"), Decimal("-1234.50"))
        self.assertEqual(to_decimal("1234-"), Decimal("-1234"))

    def test_arabic_indic_digits(self):
        self.assertEqual(to_decimal("١٢٣"), Decimal("123"))
        self.assertEqual(to_decimal("۴۵۶"), Decimal("456"))

    def test_unparseable_text_returns_none_not_zero(self):
        # Returning 0 here would silently corrupt a control total.
        for value in ("n/a", "pending", "-", "abc"):
            self.assertIsNone(to_decimal(value), f"{value!r} must not become a number")

    def test_float_avoids_binary_representation_noise(self):
        self.assertEqual(to_decimal(0.1), Decimal("0.1"))

    def test_booleans_are_not_numbers(self):
        self.assertIsNone(to_decimal(True))


class TestExcelDateSystems(unittest.TestCase):
    """Part 27.1 — the workbook decides 1900 vs 1904; never assume."""

    def test_1900_system_day_one(self):
        self.assertEqual(excel_serial_to_date(1), (1900, 1, 1))

    def test_1900_system_accounts_for_the_phantom_leap_day(self):
        # Excel believes 29 Feb 1900 existed. Serial 61 is 1 March 1900.
        self.assertEqual(excel_serial_to_date(61), (1900, 3, 1))

    def test_1900_system_matches_well_known_anchors(self):
        # These serials are widely documented, so they pin the conversion
        # against an external reference rather than against our own arithmetic.
        self.assertEqual(excel_serial_to_date(25569), (1970, 1, 1))  # Unix epoch
        self.assertEqual(excel_serial_to_date(44197), (2021, 1, 1))
        self.assertEqual(excel_serial_to_date(45292), (2024, 1, 1))

    def test_serial_60_is_the_documented_ambiguity(self):
        # Excel's phantom 29 Feb 1900 has no real calendar date, so serials 59
        # and 60 both land on 28 Feb 1900. Real business data never contains
        # 1900 dates; the quality gate's date-range check catches it if it does.
        self.assertEqual(excel_serial_to_date(59), excel_serial_to_date(60))

    def test_1904_system_differs_from_1900(self):
        self.assertNotEqual(
            excel_serial_to_date(1000, date_system_1904=False),
            excel_serial_to_date(1000, date_system_1904=True),
        )

    def test_1904_system_day_zero(self):
        self.assertEqual(excel_serial_to_date(0, date_system_1904=True), (1904, 1, 1))


if __name__ == "__main__":
    unittest.main()
