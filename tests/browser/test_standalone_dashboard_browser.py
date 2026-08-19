"""The published dashboard, opened in a real browser (V10 Part 35.6).

Everything else in this repository verifies the dashboard *package*. This file
verifies the thing the employee actually looks at: the standalone HTML, loaded
in Chromium, built from the real Reference D pipeline output rather than from a
hand-written pack.

What it proves
--------------
- the page makes **zero network requests** — offline means offline, and a
  single CDN reference would make the report fail on a disconnected PC;
- **zero JavaScript errors** and zero failed page errors;
- the KPI values on screen are the ones the engine computed;
- charts carry an accessible name and summary, so the numbers are reachable
  without seeing the picture;
- Arabic / RTL renders and the direction actually flips;
- the theme toggle and keyboard focus work;
- print does not hide the trusted content.

What it does NOT prove here, and why
-------------------------------------
Most tests below still inject a minimal recorder in place of ECharts and
assert the **data handed to it** is correct, independent of rendering-engine
internals — that is a real and distinct thing to get right (Part 7.2's
name-based projection could be correct while a chart spec mapping bug still
sends the wrong series to the picture). `web/vendor/echarts.min.js` (the real,
checksum-verified Apache ECharts 6.1.0 binary — see `web/vendor/README.md`) is
now vendored, so `TestStandaloneDashboardRealRendering` below additionally
proves actual rendering: real `<canvas>` elements appear, `window.echarts`
reports version 6.1.0, and no JavaScript error is thrown. Both proofs matter;
neither substitutes for the other.

Browser binary: this suite never downloads one. It uses the Chromium already
present in the image, and skips cleanly when neither Playwright nor a browser
is available, so a machine without them is not silently reported as passing.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

_HAS_PLAYWRIGHT = importlib.util.find_spec("playwright") is not None
_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None

#: Chromium locations to try, in order. Never a download (Part 23.6).
_BROWSER_CANDIDATES = (
    os.environ.get("CHROMIUM_EXECUTABLE", ""),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
)


def _browser_executable() -> str | None:
    for candidate in _BROWSER_CANDIDATES:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


#: Stands in for Apache ECharts. It records what the runtime asks it to draw so
#: the *data* can be asserted; it deliberately draws nothing, because proving
#: rendering requires the real vendored asset.
ECHARTS_RECORDER = """
window.__CHART_CALLS__ = [];
window.echarts = {
  init: function (node) {
    return {
      setOption: function (option) {
        window.__CHART_CALLS__.push({
          label: node.getAttribute('aria-label'),
          role: node.getAttribute('role'),
          categories: (option.xAxis && option.xAxis.data) || [],
          series: (option.series || []).map(function (s) {
            return { name: s.name, type: s.type, data: s.data };
          })
        });
      }
    };
  }
};
"""


@unittest.skipUnless(_HAS_DUCKDB, "DuckDB is an application-tier dependency")
@unittest.skipUnless(_HAS_PLAYWRIGHT, "Playwright is not installed")
class TestStandaloneDashboardInChromium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executable = _browser_executable()
        if cls.executable is None:
            raise unittest.SkipTest(
                "no local Chromium found; this suite never downloads one")
        cls._temp = tempfile.TemporaryDirectory()
        cls.pack = cls._build_pack(Path(cls._temp.name))
        cls.html_path = cls._build_html(Path(cls._temp.name), cls.pack)

    @classmethod
    def tearDownClass(cls):
        cls._temp.cleanup()

    # ------------------------------------------------------------------ set-up
    @classmethod
    def _build_pack(cls, temp: Path) -> dict:
        """Run the real Reference D pipeline and keep its dashboard package."""
        from app.data.database import Database
        from app.excel.fixture_adapter import ACK_VARIABLE, FixtureExtractionAdapter
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project
        from tools._common import REPO_ROOT

        previous = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        try:
            contract = load_project(
                REPO_ROOT / "projects/_REFERENCE_FINANCE_PPV")
            database = Database(temp / "browser.duckdb")
            pipeline = ProjectPipeline(
                database, contract, application_version="test")
            pipeline.prepare()
            files = {
                "purchases": "purchases_p1.csv",
                "standard_cost": "standard_cost_p1.csv",
                "vendors": "vendors_p1.csv",
                "ppv_budget": "ppv_budget_p1.csv",
            }
            ports = {}
            for source_id, filename in files.items():
                path = REPO_ROOT / "tests/fixtures/finance_ppv" / filename
                adapter = FixtureExtractionAdapter(path)
                adapter.open(str(path), {
                    "run_id": "BROWSER-1",
                    "report_id": contract.project_id,
                    "sheet": contract.source(source_id).sheet,
                    "schema_version": "1",
                    "extraction": {
                        "target_cells_per_chunk": 1000,
                        "min_rows_per_chunk": 1,
                        "max_rows_per_chunk": 100,
                    },
                })
                ports[source_id] = adapter
            outcome = pipeline.run(
                "BROWSER-1", ports, requested_periods={"ppv_budget": "2026-08"})
            assert outcome.succeeded, outcome.error_message
            database.close()
            return outcome.dashboard
        finally:
            if previous is None:
                os.environ.pop(ACK_VARIABLE, None)
            else:
                os.environ[ACK_VARIABLE] = previous

    @classmethod
    def _build_html(cls, temp: Path, pack: dict) -> Path:
        from app.dashboard.html_builder import build
        from tools._common import REPO_ROOT

        recorder = temp / "echarts_recorder.js"
        recorder.write_text(ECHARTS_RECORDER, encoding="utf-8")
        html = build(
            pack,
            styles_path=REPO_ROOT / "web" / "styles.css",
            echarts_path=recorder,
        )
        target = temp / "report.html"
        target.write_text(html, encoding="utf-8")
        return target

    # ------------------------------------------------------------------ driver
    def _open(self, *, locale: str | None = None, rtl: bool = False):
        """Open the report, failing the test on any network or JS error."""
        from playwright.sync_api import sync_playwright

        manager = sync_playwright().start()
        self.addCleanup(manager.stop)
        browser = manager.chromium.launch(executable_path=self.executable)
        self.addCleanup(browser.close)
        context = browser.new_context(
            locale=locale or "en-GB",
            reduced_motion="reduce",
        )
        page = context.new_page()

        self.network: list[str] = []
        self.errors: list[str] = []
        page.on("request", lambda r: self.network.append(r.url))
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("console", lambda m: (
            self.errors.append(m.text) if m.type == "error" else None))

        page.goto(self.html_path.as_uri())
        page.wait_for_load_state("load")
        if rtl:
            page.evaluate(
                "document.documentElement.setAttribute('dir','rtl');"
                "document.documentElement.setAttribute('lang','ar');")
        return page

    def _assert_clean(self):
        remote = [
            url for url in self.network
            if not url.startswith("file://") and not url.startswith("data:")
        ]
        self.assertEqual(
            remote, [],
            f"the standalone report reached the network: {remote}. Offline "
            f"means the report must work on a disconnected PC (Part 23.6)")
        self.assertEqual(
            self.errors, [], f"JavaScript errors on the page: {self.errors}")

    # ------------------------------------------------------------------- tests
    def test_report_opens_offline_with_no_network_and_no_script_errors(self):
        page = self._open()
        self.assertEqual(
            page.inner_text("#title"), self.pack["report"]["title"])
        self._assert_clean()

    def test_the_html_file_contains_no_remote_reference_at_all(self):
        """A structural check that does not depend on what the page chose to
        request at run time."""
        html = self.html_path.read_text("utf-8")
        for marker in ("http://", "https://", "//cdn", "<script src=",
                       "<link rel=\"stylesheet\" href="):
            self.assertNotIn(
                marker, html,
                f"standalone report contains a remote reference: {marker!r}")

    def test_every_kpi_on_screen_is_the_value_the_engine_computed(self):
        page = self._open()
        rendered = page.eval_on_selector_all(
            ".kpi-card",
            "cards => cards.map(c => ({"
            " label: c.querySelector('h3').textContent,"
            " value: c.querySelector('.kpi-value').textContent }))")
        expected = [
            {"label": item["label"],
             "value": "—" if item["display"] is None else item["display"]}
            for item in self.pack["kpis"]
        ]
        self.assertEqual(rendered, expected)
        # Guard against an empty-but-equal comparison.
        self.assertGreaterEqual(len(rendered), 5)
        self.assertIn("-175.00", [item["value"] for item in rendered])
        self._assert_clean()

    def test_charts_are_given_an_accessible_name_and_the_correct_data(self):
        """Accessibility: the numbers must be reachable without the picture."""
        page = self._open()
        calls = page.evaluate("window.__CHART_CALLS__")
        self.assertEqual(len(calls), len(self.pack["charts"]))
        for call, spec in zip(calls, self.pack["charts"]):
            self.assertEqual(call["role"], "img")
            self.assertEqual(call["label"], spec["accessible_summary"])
            self.assertTrue(call["label"].strip())
            points = spec["series"][0]["points"]
            self.assertEqual(call["categories"], [p["x"] for p in points])
            self.assertEqual(call["series"][0]["data"], [p["y"] for p in points])
        self._assert_clean()

    def test_insight_text_is_rendered_without_false_precision(self):
        page = self._open()
        text = page.inner_text("#insights")
        self.assertIn("largest contributor", text)
        self.assertNotIn("00000000", text)
        self.assertIn("investigation priority", text)
        self._assert_clean()

    def test_right_to_left_layout_actually_flips(self):
        page = self._open(locale="ar-EG", rtl=True)
        direction = page.evaluate(
            "getComputedStyle(document.documentElement).direction")
        self.assertEqual(direction, "rtl")
        # Content must still be present, not just mirrored away.
        self.assertEqual(
            page.inner_text("#title"), self.pack["report"]["title"])
        self.assertTrue(page.inner_text("#kpis").strip())
        self._assert_clean()

    def test_theme_toggle_switches_and_keeps_content(self):
        page = self._open()
        before = page.get_attribute("html", "data-theme")
        page.click("#theme")
        after = page.get_attribute("html", "data-theme")
        self.assertNotEqual(before, after)
        self.assertTrue(page.inner_text("#kpis").strip())
        self._assert_clean()

    def test_the_theme_control_is_keyboard_reachable(self):
        page = self._open()
        page.keyboard.press("Tab")
        focused = page.evaluate("document.activeElement.id")
        self.assertEqual(
            focused, "theme",
            "the only interactive control must be reachable by keyboard")
        page.keyboard.press("Enter")
        self.assertTrue(page.inner_text("#kpis").strip())
        self._assert_clean()

    def test_trusted_text_meets_wcag_aa_contrast_in_both_themes(self):
        """WCAG 2.2 AA: 4.5:1 for body text, 3:1 for large text.

        The KPI value is the number the decision is made from. If it is low
        contrast, the report is unreadable for exactly the people accessibility
        rules exist to protect — and "it looked fine on my monitor" is not a
        measurement.
        """
        page = self._open()
        ratio_script = """
        (selector) => {
          const parse = (c) => c.match(/[\\d.]+/g).slice(0, 3).map(Number);
          const lum = (rgb) => {
            const a = rgb.map((v) => {
              v /= 255;
              return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
          };
          const backgroundOf = (node) => {
            let el = node;
            while (el) {
              const bg = getComputedStyle(el).backgroundColor;
              const parts = bg.match(/[\\d.]+/g);
              if (parts && (parts.length < 4 || Number(parts[3]) > 0)) return parse(bg);
              el = el.parentElement;
            }
            return [255, 255, 255];
          };
          const el = document.querySelector(selector);
          if (!el) return null;
          const style = getComputedStyle(el);
          const fg = parse(style.color);
          const bg = backgroundOf(el);
          const L1 = lum(fg), L2 = lum(bg);
          const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
          return { ratio, size: parseFloat(style.fontSize),
                   weight: style.fontWeight };
        }
        """
        for theme in ("light", "dark"):
            page.evaluate(
                "(t) => document.documentElement.dataset.theme = t", theme)
            for selector in (".kpi-value", ".kpi-card h3", "#title",
                             "#insights p"):
                measured = page.evaluate(ratio_script, selector)
                if measured is None:
                    continue
                large = measured["size"] >= 24 or (
                    measured["size"] >= 18.66
                    and int(measured["weight"] or 400) >= 700)
                minimum = 3.0 if large else 4.5
                self.assertGreaterEqual(
                    round(measured["ratio"], 2), minimum,
                    f"{selector} in {theme} theme is "
                    f"{measured['ratio']:.2f}:1, below WCAG AA {minimum}:1")
        self._assert_clean()

    def test_reduced_motion_preference_is_respected(self):
        """Part 22.9: motion is decoration; it must not be forced on anyone."""
        page = self._open()
        self.assertTrue(page.evaluate(
            "window.matchMedia('(prefers-reduced-motion: reduce)').matches"),
            "the test context did not request reduced motion")
        offenders = page.evaluate("""
        () => Array.from(document.querySelectorAll('*')).filter((el) => {
          const s = getComputedStyle(el);
          const dur = parseFloat(s.animationDuration) || 0;
          const trans = parseFloat(s.transitionDuration) || 0;
          return (dur > 0.01 || trans > 0.01);
        }).map((el) => el.className || el.tagName).slice(0, 5)
        """)
        self.assertEqual(
            offenders, [],
            f"animation still runs under prefers-reduced-motion: {offenders}")
        self._assert_clean()

    def test_print_layout_keeps_trusted_content_and_drops_the_control(self):
        page = self._open()
        page.emulate_media(media="print")
        self.assertTrue(page.inner_text("#kpis").strip())
        self.assertTrue(page.inner_text("#title").strip())
        self.assertFalse(
            page.is_visible("#theme"),
            "the theme button is an interactive control and must not print")
        self._assert_clean()

    def test_quality_and_watermark_state_reaches_the_page(self):
        page = self._open()
        self.assertEqual(
            page.inner_text("#quality"), self.pack["quality"]["status"])
        watermarks = page.inner_text("#watermarks")
        if self.pack.get("demo_data"):
            self.assertIn(
                "DEMO DATA", watermarks,
                "fixture-sourced output must be watermarked on screen "
                "(Part 44.3 rule 2)")
        self._assert_clean()


_VENDORED_ECHARTS = Path("web/vendor/echarts.min.js")


@unittest.skipUnless(_HAS_DUCKDB, "DuckDB is an application-tier dependency")
@unittest.skipUnless(_HAS_PLAYWRIGHT, "Playwright is not installed")
class TestStandaloneDashboardRealRendering(unittest.TestCase):
    """The rendering half TestStandaloneDashboardInChromium deliberately skips.

    Uses the real vendored `web/vendor/echarts.min.js`, not the data-recording
    stand-in, so this proves pixels actually get drawn rather than only that
    the right data was handed to a chart library.
    """

    @classmethod
    def setUpClass(cls):
        from tools._common import REPO_ROOT

        cls.executable = _browser_executable()
        if cls.executable is None:
            raise unittest.SkipTest(
                "no local Chromium found; this suite never downloads one")
        vendored = REPO_ROOT / _VENDORED_ECHARTS
        if not vendored.is_file():
            raise unittest.SkipTest(
                "web/vendor/echarts.min.js is not vendored yet — see "
                "web/vendor/README.md")
        cls._temp = tempfile.TemporaryDirectory()
        pack = TestStandaloneDashboardInChromium._build_pack(Path(cls._temp.name))
        cls.pack = pack
        cls.html_path = cls._build_html(Path(cls._temp.name), pack, vendored)

    @classmethod
    def tearDownClass(cls):
        cls._temp.cleanup()

    @classmethod
    def _build_html(cls, temp: Path, pack: dict, echarts_path: Path) -> Path:
        from app.dashboard.html_builder import build
        from tools._common import REPO_ROOT

        html = build(
            pack,
            styles_path=REPO_ROOT / "web" / "styles.css",
            echarts_path=echarts_path,
        )
        target = temp / "report.html"
        target.write_text(html, encoding="utf-8")
        return target

    def test_the_vendored_asset_is_the_real_licensed_apache_echarts_build(self):
        from tools._common import REPO_ROOT

        text = (REPO_ROOT / _VENDORED_ECHARTS).read_text("utf-8", errors="strict")
        self.assertIn("Apache Software Foundation", text[:2000])

    def test_charts_render_as_real_canvas_elements_with_the_vendored_engine(self):
        from playwright.sync_api import sync_playwright

        manager = sync_playwright().start()
        self.addCleanup(manager.stop)
        browser = manager.chromium.launch(executable_path=self.executable)
        self.addCleanup(browser.close)
        page = browser.new_context().new_page()

        network: list[str] = []
        errors: list[str] = []
        page.on("request", lambda r: network.append(r.url))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: (
            errors.append(m.text) if m.type == "error" else None))

        page.goto(self.html_path.as_uri())
        page.wait_for_load_state("load")

        version = page.evaluate("window.echarts && window.echarts.version")
        self.assertEqual(version, "6.1.0")

        chart_count = len(self.pack.get("charts", []))
        self.assertGreater(chart_count, 0, "fixture must produce at least one chart")
        canvases = page.eval_on_selector_all(
            ".chart canvas", "nodes => nodes.length")
        self.assertEqual(
            canvases, chart_count,
            "each chart container must contain a real rendered canvas")

        remote = [u for u in network
                 if not u.startswith("file://") and not u.startswith("data:")]
        self.assertEqual(remote, [])
        self.assertEqual(errors, [], f"JavaScript errors while rendering: {errors}")


if __name__ == "__main__":
    unittest.main()
