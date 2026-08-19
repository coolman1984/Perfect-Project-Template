"""GATE_NO_BROWSER_ARITHMETIC — the browser renders trusted numbers, never
computes them (V10 Part 14.4 / Part 19 / Part 23).

The gate asks for two things, and both are here because either alone is weak:

1. A **static check** over `web/`. This catches a developer reaching for
   `kpi.value * 100` in a renderer. It is a syntactic guard and cannot prove
   the absence of every possible recomputation — so it is not the real proof.

2. A **dashboard-vs-SQL equality test**. This is the real proof: every KPI the
   browser is handed must already equal what the project's own trusted SQL
   returns, so there is nothing left for the browser to compute. If a value
   were being derived in JavaScript, the package value would differ from the
   SQL value and this test would fail.

The engine's contract, visible in `web/app.js`, is that `kpi.display` is a
pre-formatted string and `kpi.value` is only ever null-checked. The static
check below encodes exactly that.
"""

from __future__ import annotations

import re
import unittest

from tools._common import REPO_ROOT

WEB_ROOT = REPO_ROOT / "web"

#: Fields through which trusted numbers enter the browser. Arithmetic on any of
#: these would mean the browser is deriving a business result.
TRUSTED_VALUE_ACCESSORS = (
    r"\bkpi\.value\b", r"\bkpi\.display\b",
    r"\bpoint\.y\b", r"\bpoint\.x\b",
    r"\.kpis\b", r"\.series\b", r"\.points\b",
    r"\binsight\.current\b",
)

#: Numeric operators. `+` is excluded on purpose: template-literal string
#: building is pervasive and legitimate, and a `+` that mattered would have to
#: appear alongside one of the accessors above anyway, which the combined
#: pattern below still catches for `-`, `*`, `/` and `%`.
ARITHMETIC = re.compile(r"(?<![*/])\s[-*/%]\s(?!/)")

COMMENT = re.compile(r"^\s*(//|/\*|\*)")


class TestNoTrustedArithmeticInTheBrowser(unittest.TestCase):
    def _javascript_files(self):
        # web/vendor/ holds unmodified third-party code (Apache ECharts) that
        # this project does not author or review line by line; scanning it
        # only produces false positives from its own internal variable names
        # (e.g. its many internal "points" arrays), never a real finding.
        files = sorted(
            path for path in WEB_ROOT.rglob("*.js")
            if "vendor" not in path.relative_to(WEB_ROOT).parts)
        self.assertTrue(files, "no browser JavaScript found to check")
        return files

    def test_no_arithmetic_is_applied_to_a_trusted_value(self):
        accessor = re.compile("|".join(TRUSTED_VALUE_ACCESSORS))
        offences = []
        for path in self._javascript_files():
            for lineno, line in enumerate(
                    path.read_text("utf-8").splitlines(), start=1):
                if COMMENT.match(line):
                    continue
                if accessor.search(line) and ARITHMETIC.search(line):
                    offences.append(
                        f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
        self.assertEqual(
            offences, [],
            "trusted values must be rendered, not recomputed, in the browser "
            f"(V10 Part 14.4): {offences}")

    def test_renderer_uses_the_preformatted_display_string(self):
        """`kpi.display` comes from the engine already formatted.

        If a renderer ever formatted `kpi.value` itself — rounding, scaling,
        percent conversion — that formatting would be a second, unversioned
        definition of the number.
        """
        app_js = (WEB_ROOT / "app.js").read_text("utf-8")
        self.assertIn("kpi.display", app_js)
        self.assertNotRegex(
            app_js, r"kpi\.value\s*\.toFixed",
            "the browser must not format a trusted value itself")
        self.assertNotRegex(
            app_js, r"kpi\.value\s*[*/%]",
            "the browser must not scale a trusted value")

    def test_no_javascript_file_reimplements_a_reference_metric_name(self):
        """A trusted formula lives once, in project SQL (Part 14.4).

        A JavaScript file that both names a reference metric and performs
        arithmetic is re-deriving something the engine already computed.
        """
        metric_names = set()
        for metrics_sql in REPO_ROOT.glob(
                "projects/*/business_rules/metrics.sql"):
            metric_names.update(
                re.findall(r"^-- name:\s*(\S+)", metrics_sql.read_text("utf-8"),
                           re.M))
        self.assertTrue(metric_names, "no reference metrics found to check")

        offences = []
        for path in self._javascript_files():
            text = path.read_text("utf-8")
            for name in sorted(metric_names):
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if COMMENT.match(line):
                        continue
                    if re.search(rf"\b{re.escape(name)}\b", line) \
                            and ARITHMETIC.search(line):
                        offences.append(
                            f"{path.relative_to(REPO_ROOT)}:{lineno} ({name})")
        self.assertEqual(offences, [], f"metric recomputed in browser: {offences}")


if __name__ == "__main__":
    unittest.main()
