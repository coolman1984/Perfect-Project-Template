"""Regressions for defects found in the full-project bug sweep.

Each test pins one fixed bug. They are grouped here rather than scattered so
the sweep's findings stay visible as a set — several were the same mistake in
different tools, which is the pattern worth noticing (lessons L-007, L-008).
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from app.excel.conversion import to_decimal
from tools._common import REPO_ROOT
from tools._miniyaml import dump_records, load_records


class TestDecimalLocaleAmbiguity(unittest.TestCase):
    """Was: `1.234,56` silently parsed as 1.23456 — a corrupted control total.

    Constitution 27.3 requires an explicit locale parser and quarantined
    ambiguity, not a guess.
    """

    def test_both_separators_rightmost_wins_regardless_of_locale(self):
        # Grouping never follows the decimal point, so this needs no config.
        self.assertEqual(to_decimal("1.234,56"), Decimal("1234.56"))
        self.assertEqual(to_decimal("1,234.56"), Decimal("1234.56"))
        self.assertEqual(to_decimal("1.234,56", decimal_separator=","), Decimal("1234.56"))

    def test_valid_grouping_is_accepted(self):
        self.assertEqual(to_decimal("1,234"), Decimal("1234"))
        self.assertEqual(to_decimal("1,234,567"), Decimal("1234567"))

    def test_ambiguous_single_separator_is_quarantined_not_guessed(self):
        # "1,5" is 15 in no locale. It is 1.5 (de-DE) or malformed (en-US).
        # Returning a number here is how a control total silently goes wrong.
        for text in ("1,5", "1,23", "1,23456"):
            self.assertIsNone(to_decimal(text), f"{text!r} must not be guessed")

    def test_european_locale_parses_its_own_format(self):
        self.assertEqual(to_decimal("1,5", decimal_separator=","), Decimal("1.5"))
        self.assertEqual(to_decimal("1,234", decimal_separator=","), Decimal("1.234"))

    def test_malformed_grouping_is_rejected(self):
        self.assertIsNone(to_decimal("1,23,456"))
        self.assertIsNone(to_decimal("1.2.3"))

    def test_previously_correct_behaviour_is_preserved(self):
        self.assertEqual(to_decimal("(1,234.50)"), Decimal("-1234.50"))
        self.assertEqual(to_decimal("1234.5"), Decimal("1234.5"))
        self.assertEqual(to_decimal("\u0661\u0662\u0663"), Decimal("123"))
        self.assertIsNone(to_decimal("n/a"))


class TestMiniYamlRoundTrip(unittest.TestCase):
    """Was: dump escaped `"` but load never unescaped it, so every save/load
    cycle added a backslash to any ledger value containing a quote."""

    def test_values_survive_a_round_trip(self):
        cases = [
            {"id": "A", "v": "plain"},
            {"id": "B", "v": "has: colon"},
            {"id": "C", "v": 'has "double quotes" inside'},
            {"id": "D", "v": "has 'single' quotes"},
            {"id": "E", "v": "hash # inside"},
            {"id": "F", "v": ""},
        ]
        self.assertEqual(load_records(dump_records(cases)), cases)

    def test_repeated_cycles_do_not_accumulate_escapes(self):
        record = [{"id": "A", "v": 'a "quoted" value'}]
        text = dump_records(record)
        for _ in range(3):
            text = dump_records(load_records(text))
        self.assertEqual(load_records(text), record)


class TestGateLedgerHygiene(unittest.TestCase):
    """Was: gates that had passed still prescribed a next_action, which reads
    as unfinished work and erodes trust in the ledger."""

    def test_settled_gates_carry_no_next_action(self):
        from tools import gates

        for record in gates.load_ledger():
            if record.get("status") in ("pass", "not_applicable"):
                self.assertEqual(
                    record.get("next_action", "").strip(), "",
                    f"{record['id']} is settled but still prescribes an action")


class TestApprovalLookupCoversEverySection(unittest.TestCase):
    """Was: the lookup checked only [history] and [quality], so
    `storage_allowed` in [output] — the IT-approved location required by
    Part 13.5 — was never validated."""

    def test_finds_keys_in_any_section(self):
        from tools.report_tool import _lookup_config_value

        config = {
            "load_mode": "upsert",
            "history": {"business_key": ["a"]},
            "quality": {"control_total_column": "qty"},
            "output": {"storage_allowed": ["D:/secure"]},
        }
        self.assertEqual(_lookup_config_value(config, "load_mode"), "upsert")
        self.assertEqual(_lookup_config_value(config, "business_key"), ["a"])
        self.assertEqual(_lookup_config_value(config, "control_total_column"), "qty")
        self.assertEqual(_lookup_config_value(config, "storage_allowed"), ["D:/secure"])
        self.assertIsNone(_lookup_config_value(config, "not_present"))

    def test_every_declared_approval_resolves_in_the_template(self):
        import tomllib

        from tools.report_tool import _lookup_config_value

        config = tomllib.loads((REPO_ROOT / "reports/_TEMPLATE/report.toml").read_text())
        for key in config.get("approvals", {}):
            self.assertIsNotNone(
                _lookup_config_value(config, key),
                f"approval '{key}' is declared but its value cannot be found")


class TestWindowsLauncherLineEndings(unittest.TestCase):
    """Was: every .bat shipped with LF. cmd.exe can mis-parse LF-only batch
    files, and the employee runtime is Windows-only."""

    def test_every_bat_file_uses_crlf(self):
        for path in sorted(REPO_ROOT.glob("*.bat")):
            data = path.read_bytes()
            stray = data.replace(b"\r\n", b"").count(b"\n")
            self.assertEqual(stray, 0, f"{path.name} contains bare LF line endings")

    def test_gitattributes_pins_bat_to_crlf(self):
        attributes = (REPO_ROOT / ".gitattributes").read_text()
        self.assertIn("*.bat", attributes)
        self.assertIn("eol=crlf", attributes)

    def test_shell_scripts_stay_lf(self):
        for path in sorted(REPO_ROOT.glob("*.sh")):
            self.assertNotIn(b"\r\n", path.read_bytes(), f"{path.name} must stay LF")


class TestExitCodeContract(unittest.TestCase):
    """Part 37.4: 2 means usage error, 1 means a real violation. Conflating
    them tells an agent it broke something when it only mistyped a flag."""

    def _run(self, *args: str) -> int:
        return subprocess.run(
            [sys.executable, "tools/project_tool.py", *args],
            cwd=REPO_ROOT, capture_output=True, text=True).returncode

    def test_out_of_range_budget_is_a_usage_error(self):
        self.assertEqual(self._run("map", "context", "--task", "x", "--budget", "50"), 2)

    def test_group_without_command_is_a_usage_error(self):
        self.assertEqual(self._run("map"), 2)

    def test_valid_invocation_passes(self):
        # Deliberately a command that depends only on committed content.
        # `map verify` would also work, but it fails whenever the working tree
        # is mid-edit, which would make this test fail for the wrong reason.
        self.assertEqual(self._run("constitution", "audit"), 0)


class TestNotImplementedContract(unittest.TestCase):
    """Part 37.3: an unimplemented command must exit non-zero and name its
    file. This exercises the helper so the contract cannot rot unnoticed."""

    def test_helper_fails_loudly_and_names_the_file(self):
        import io
        from contextlib import redirect_stdout

        from tools._common import EXIT_FAIL, not_implemented

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = not_implemented("map explode", "tools/project_map.py")
        output = buffer.getvalue()

        self.assertEqual(code, EXIT_FAIL)
        self.assertIn("TOOL_COMMAND_NOT_IMPLEMENTED", output)
        self.assertIn("tools/project_map.py", output)


if __name__ == "__main__":
    unittest.main()
