"""Half of GATE_NO_CELL_BY_CELL: the static guard (V10 Part 9 / Part 16.2).

Reading a protected workbook cell by cell means one COM border crossing per
cell. Twenty million cells that way takes hours; one rectangular `Range.Value2`
read takes seconds. So per-cell COM access is a release-blocking violation, not
a performance preference.

**This file cannot close the gate on its own, and does not claim to.** The
production COM adapter (`app/excel/com_adapter.py`, plus `session.py`,
`discovery.py`, `extractor.py`) was written on 2026-08-19, so the static half
of the gate now runs against real extraction code rather than stubs. The gate's
second half — a measured block-vs-per-cell benchmark on a real workbook — still
requires the authorized Windows machine and remains open.

What this file does is keep the rule enforceable as that code changes: the
checks below run over whatever `app/excel/` contains, so the first per-cell loop
added to the implementation fails CI rather than being discovered on a
20-million-cell workbook.
"""

from __future__ import annotations

import ast
import re
import unittest

from tools._common import REPO_ROOT

EXCEL_ROOT = REPO_ROOT / "app" / "excel"

#: COM member access that reads one cell at a time.
PER_CELL_ACCESS = re.compile(
    r"\.Cells\s*\(|\.Item\s*\(\s*\w+\s*,\s*\w+\s*\)|\.Range\s*\(\s*[\"']?[A-Z]{1,3}\d+[\"']?\s*\)\s*\.\s*Value",
    re.IGNORECASE)

COMMENT_OR_DOC = re.compile(r"^\s*(#|\"\"\"|''')")


def _code_lines(path):
    """Yield (lineno, line) skipping comments and docstring bodies.

    The module docstrings in this package deliberately *describe* the forbidden
    pattern in prose, so a naive scan would flag the very rules it enforces.
    """
    text = path.read_text("utf-8")
    tree = ast.parse(text)
    docstring_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc and node.body:
                first = node.body[0]
                docstring_lines.update(
                    range(first.lineno, (first.end_lineno or first.lineno) + 1))
    for lineno, line in enumerate(text.splitlines(), start=1):
        if lineno in docstring_lines or COMMENT_OR_DOC.match(line):
            continue
        yield lineno, line


class TestNoPerCellComAccess(unittest.TestCase):
    def _python_files(self):
        files = sorted(EXCEL_ROOT.glob("*.py"))
        self.assertTrue(files, "no extraction modules found to check")
        return files

    def test_no_module_reads_excel_cell_by_cell(self):
        offences = []
        for path in self._python_files():
            for lineno, line in _code_lines(path):
                if PER_CELL_ACCESS.search(line):
                    offences.append(
                        f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
        self.assertEqual(
            offences, [],
            "per-cell COM access is a release blocker; read rectangular "
            f"Range.Value2 blocks instead (V10 Part 9): {offences}")

    def test_no_nested_row_and_column_loop_indexes_a_worksheet(self):
        """A doubly-nested loop over rows and columns is the shape a per-cell
        read takes even when it avoids the `.Cells(` spelling."""
        offences = []
        for path in self._python_files():
            tree = ast.parse(path.read_text("utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.For):
                    continue
                for inner in ast.walk(node):
                    if inner is node or not isinstance(inner, ast.For):
                        continue
                    for call in ast.walk(inner):
                        if isinstance(call, ast.Attribute) and call.attr in (
                                "Value", "Value2", "Cells", "Item"):
                            offences.append(
                                f"{path.relative_to(REPO_ROOT)}:{inner.lineno}")
        self.assertEqual(
            offences, [],
            f"nested row/column loop reading worksheet values: {offences}")

    def test_the_com_adapter_still_documents_the_block_read_requirement(self):
        """The rule must survive in the place the implementer will read.

        This is what carries the requirement forward while the adapter is a
        stub: whoever implements it sees the constraint in the docstring they
        are replacing.
        """
        text = (EXCEL_ROOT / "com_adapter.py").read_text("utf-8")
        self.assertIn("Value2", text)
        self.assertIn("rows_per_chunk", text)
        self.assertRegex(text, r"per-cell loop|cell-by-cell|per-cell")

    def test_production_extraction_is_written(self):
        """Pins the honest status this gate depends on.

        This replaces an earlier assertion that all four modules were stubs.
        They were written on 2026-08-19; the assertion is inverted rather than
        deleted so the file keeps stating a checkable fact about the adapter's
        status instead of quietly losing the claim.
        """
        for name in ("com_adapter", "extractor", "session", "discovery"):
            text = (EXCEL_ROOT / f"{name}.py").read_text("utf-8")
            self.assertNotIn(
                "NotImplementedError", text,
                f"app/excel/{name}.py regressed to a stub; production "
                f"extraction is written and CURRENT_STATE.md says so")

    def test_only_the_permitted_modules_import_com(self):
        """Part 44.2, checked here as well as in the source scanner.

        `discovery` and `extractor` hold the rules most likely to be wrong —
        bounds, chunk arithmetic, column mapping. Keeping COM out of them is
        what lets those rules run in CI on Linux, so it is worth failing a test
        over and not only a scanner pass.
        """
        permitted = {"com_adapter.py", "session.py"}
        for path in self._python_files():
            if path.name in permitted:
                continue
            for lineno, line in _code_lines(path):
                self.assertNotRegex(
                    line, r"\b(import\s+win32|from\s+win32|import\s+pythoncom)\b",
                    f"{path.relative_to(REPO_ROOT)}:{lineno} imports COM "
                    f"outside {sorted(permitted)} (Part 44.2)")

    def test_the_protected_file_gate_is_not_claimed_by_this_suite(self):
        """Writing the adapter does not close GATE_PROTECTED_FILE_PROOF.

        Part 44.3 rule 3: only a real COM read of a real DRM-protected workbook
        on the authorized machine advances that gate. No amount of unprotected
        or fixture testing substitutes, and this test exists so that confusion
        cannot creep back in as the adapter matures.
        """
        text = (EXCEL_ROOT / "com_adapter.py").read_text("utf-8")
        self.assertIn("GATE_PROTECTED_FILE_PROOF", text)
        self.assertRegex(text, r"remains open|cannot close it|still open")


if __name__ == "__main__":
    unittest.main()
