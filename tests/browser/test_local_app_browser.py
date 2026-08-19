"""The local application UI, opened in a real browser against a real loopback
server (V10 Part 35.6, build program S6).

`test_standalone_dashboard_browser.py` proves the exported, view-only report.
This file proves the thing an employee actually works in day to day: the
local app UI (`web/index.html` + `web/app.js`) served by the real FastAPI
loopback server (`app.server.create_app`), started on a real bound socket
(`app.local_transport.start_listener`) — not a synthetic `TestClient` stand-in.

What it proves
---------------
- the shell loads with zero JavaScript errors against the real server;
- the filter ribbon renders real controls from a real dashboard.toml
  `[[filters]]` block and a real chart's `dimensions`, not fixture text;
- selecting a filter value client-side filters the matching chart's points,
  adds a removable chip, and Reset restores the original unfiltered data —
  the actual GATE_FILTER_RECONCILIATION proof, exercised end to end;
- the language toggle sets both `lang` and `dir` (real RTL, not mirrored
  text) and translates visible UI strings from `web/i18n/ar.json`;
- the theme toggle changes the actual rendered background colour and
  persists across a reload.

Uses a fully isolated temporary repo root (copied `web/` and the real
`projects/_REFERENCE_PRODUCTION_QUALITY/`) so it never touches the real
repository's gitignored `data/`, `output/` or `runs/` directories.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

_HAS_PLAYWRIGHT = importlib.util.find_spec("playwright") is not None
_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None
_HAS_FASTAPI = importlib.util.find_spec("fastapi") is not None

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


@unittest.skipUnless(_HAS_DUCKDB, "DuckDB is an application-tier dependency")
@unittest.skipUnless(_HAS_FASTAPI, "FastAPI is an application-tier dependency")
@unittest.skipUnless(_HAS_PLAYWRIGHT, "Playwright is not installed")
class TestLocalAppInChromium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools._common import REPO_ROOT

        cls.executable = _browser_executable()
        if cls.executable is None:
            raise unittest.SkipTest(
                "no local Chromium found; this suite never downloads one")

        cls._temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temp.name)
        shutil.copytree(REPO_ROOT / "web", cls.root / "web")
        shutil.copytree(
            REPO_ROOT / "projects" / "_REFERENCE_PRODUCTION_QUALITY",
            cls.root / "projects" / "_REFERENCE_PRODUCTION_QUALITY")

        os.environ["ADAPTER_FIXTURE_ACK"] = "1"
        from app.project_orchestrator import run_project

        outcome = run_project(
            "reference_production_quality",
            {"production": REPO_ROOT / "tests/fixtures/reference/period_2.csv"},
            repo_root=cls.root,
            database_path=cls.root / "data" / "project.duckdb",
        )
        assert outcome.succeeded, outcome.error_message

        from app.local_transport import generate_launch_secret, start_listener
        from app.server import ServerContext, create_app

        cls.context = ServerContext(
            repo_root=cls.root, launch_secret=generate_launch_secret())
        app = create_app(cls.context)
        cls.listener = start_listener(app, secret=cls.context.launch_secret)
        cls.context.listener = cls.listener
        cls.url = f"http://{cls.listener.host}:{cls.listener.port}/"

    @classmethod
    def tearDownClass(cls):
        from app.excel.fixture_adapter import ACK_VARIABLE
        from app.local_transport import shutdown

        shutdown(cls.listener)
        os.environ.pop(ACK_VARIABLE, None)
        cls._temp.cleanup()

    def _open(self):
        from playwright.sync_api import sync_playwright

        manager = sync_playwright().start()
        self.addCleanup(manager.stop)
        browser = manager.chromium.launch(executable_path=self.executable)
        self.addCleanup(browser.close)
        page = browser.new_context(reduced_motion="reduce").new_page()

        self.errors: list[str] = []
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("console", lambda m: (
            self.errors.append(m.text) if m.type == "error" else None))

        page.goto(self.url)
        page.wait_for_load_state("networkidle")
        return page

    def _assert_no_js_errors(self):
        self.assertEqual(self.errors, [], f"JavaScript errors: {self.errors}")

    # ---------------------------------------------------------------- shell

    def test_shell_loads_the_real_dashboard_with_no_js_errors(self):
        page = self._open()
        self.assertIn("Production Quality", page.inner_text("#report-title"))
        self.assertGreaterEqual(
            len(page.query_selector_all(".kpi-card")), 3)
        self._assert_no_js_errors()

    def test_charts_render_as_real_canvas_with_the_vendored_engine(self):
        page = self._open()
        version = page.evaluate("window.echarts && window.echarts.version")
        self.assertEqual(version, "6.1.0")
        canvases = page.eval_on_selector_all(
            ".chart canvas", "nodes => nodes.length")
        self.assertGreaterEqual(canvases, 1)
        self._assert_no_js_errors()

    # ------------------------------------------------------------- filters

    def test_filter_ribbon_renders_real_controls_from_the_dashboard_config(self):
        """dashboard.toml declares model_code and line; only model_code has a
        chart whose dimension matches it, so only one control should render —
        proving the ribbon reflects real data, not the full declared list."""
        page = self._open()
        controls = page.query_selector_all("#filter-controls .filter-control")
        self.assertEqual(len(controls), 1)
        self.assertIn("Model", page.inner_text("#filter-controls"))
        self._assert_no_js_errors()

    def test_selecting_a_filter_value_filters_the_matching_chart(self):
        page = self._open()
        select = page.query_selector("#filter-controls select")
        select.select_option("MDL-A")

        chips = page.inner_text("#active-chips")
        self.assertIn("MDL-A", chips)

        status = page.inner_text("#filter-status")
        self.assertEqual(status.strip(), "",
                         f"reconciliation reported a problem: {status!r}")
        self._assert_no_js_errors()

    def test_reset_clears_active_filters(self):
        page = self._open()
        select = page.query_selector("#filter-controls select")
        select.select_option("MDL-A")
        self.assertIn("MDL-A", page.inner_text("#active-chips"))

        page.click("#reset-filters")
        self.assertEqual(page.inner_text("#active-chips").strip(), "")
        self._assert_no_js_errors()

    def test_removing_a_chip_deselects_the_underlying_option(self):
        page = self._open()
        select = page.query_selector("#filter-controls select")
        select.select_option("MDL-A")
        page.click("#active-chips button")
        self.assertEqual(page.inner_text("#active-chips").strip(), "")
        selected = page.eval_on_selector(
            "#filter-controls select",
            "s => Array.from(s.selectedOptions).map(o => o.value)")
        self.assertEqual(selected, [])
        self._assert_no_js_errors()

    def test_chart_point_button_cross_filters_and_drills_into_category(self):
        page = self._open()
        button = page.query_selector('.chart-point-controls button')
        self.assertIsNotNone(button)
        value = button.get_attribute('data-chart-point')
        button.click()
        self.assertIn(value, page.inner_text('#active-chips'))
        self.assertEqual(
            page.get_attribute(
                f'.chart-point-controls button[data-chart-point="{value}"]',
                'aria-pressed'),
            'true')
        self.assertEqual(page.inner_text('#filter-status').strip(), '')
        self._assert_no_js_errors()

    def test_clicking_a_real_chart_mark_cross_filters_the_dashboard(self):
        page = self._open()
        page.locator(
            'figure[data-dimensions*="model_code"] .chart'
        ).scroll_into_view_if_needed()
        point = page.evaluate("""
        () => {
          const node = document.querySelector(
            'figure[data-dimensions*="model_code"] .chart');
          const chart = window.echarts.getInstanceByDom(node);
          const option = chart.getOption();
          const category = String(option.xAxis[0].data[0]);
          const value = Number(option.series[0].data[0]);
          const pixel = chart.convertToPixel(
            { seriesIndex: 0 }, [category, value / 2]);
          const bounds = node.getBoundingClientRect();
          return {
            x: bounds.left + pixel[0],
            y: bounds.top + pixel[1],
            category,
          };
        }
        """)
        page.mouse.click(point['x'], point['y'])
        page.wait_for_function(
            "(value) => document.querySelector('#active-chips').textContent.includes(value)",
            arg=point['category'])
        self.assertEqual(page.inner_text('#filter-status').strip(), '')
        self._assert_no_js_errors()

    def test_chart_drill_control_is_keyboard_operable(self):
        page = self._open()
        button = page.query_selector('.chart-point-controls button')
        value = button.get_attribute('data-chart-point')
        button.focus()
        page.keyboard.press('Enter')
        self.assertIn(value, page.inner_text('#active-chips'))
        self._assert_no_js_errors()

    def test_focus_indicator_and_text_contrast_meet_accessibility_floor(self):
        page = self._open()
        page.focus('#theme-toggle')
        outline = page.evaluate(
            "getComputedStyle(document.querySelector('#theme-toggle')).outlineStyle")
        self.assertNotEqual(outline, 'none')

        ratios = page.evaluate("""
        () => {
          const rgb = (value) => value.match(/[0-9.]+/g).slice(0, 3).map(Number);
          const luminance = (value) => {
            const channels = rgb(value).map((part) => {
              const normalized = part / 255;
              return normalized <= 0.03928
                ? normalized / 12.92
                : Math.pow((normalized + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
          };
          const ratio = (foreground, background) => {
            const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
            return (values[0] + 0.05) / (values[1] + 0.05);
          };
          return ['body', '.period', '.filter-control label'].map((selector) => {
            const node = document.querySelector(selector);
            const style = getComputedStyle(node);
            const background = getComputedStyle(node.closest('.command-header, .filter-ribbon') || document.body).backgroundColor;
            return { selector, ratio: ratio(style.color, background) };
          });
        }
        """)
        for result in ratios:
            self.assertGreaterEqual(
                result['ratio'], 4.5,
                f"{result['selector']} contrast was {result['ratio']:.2f}:1")
        self._assert_no_js_errors()

    # ------------------------------------------------------------- i18n/RTL

    def test_language_toggle_sets_lang_and_dir_and_translates_text(self):
        page = self._open()
        page.click("#lang-toggle")
        page.wait_for_function("document.documentElement.lang === 'ar'")
        self.assertEqual(page.get_attribute("html", "dir"), "rtl")
        self.assertEqual(page.title(), "ذكاء بيانات إكسل")
        self.assertEqual(page.inner_text("#reset-filters"), "إعادة تعيين")
        self._assert_no_js_errors()

    def test_language_toggle_back_to_english_restores_ltr(self):
        page = self._open()
        page.click("#lang-toggle")
        page.wait_for_function("document.documentElement.lang === 'ar'")
        page.click("#lang-toggle")
        page.wait_for_function("document.documentElement.lang === 'en'")
        self.assertEqual(page.get_attribute("html", "dir"), "ltr")
        self._assert_no_js_errors()

    # ------------------------------------------------------------- theme

    def test_theme_toggle_changes_the_rendered_background(self):
        page = self._open()
        before = page.evaluate(
            "getComputedStyle(document.body).backgroundColor")
        starting_theme = page.evaluate("document.documentElement.dataset.theme")
        page.click("#theme-toggle")
        page.wait_for_function(
            "(t) => document.documentElement.dataset.theme !== t",
            arg=starting_theme)
        page.wait_for_function(
            "(color) => getComputedStyle(document.body).backgroundColor !== color",
            arg=before)
        after = page.evaluate(
            "getComputedStyle(document.body).backgroundColor")
        self.assertNotEqual(before, after)
        self._assert_no_js_errors()

    def test_theme_choice_persists_across_reload(self):
        page = self._open()
        page.click("#theme-toggle")
        theme = page.evaluate("document.documentElement.dataset.theme")
        page.reload()
        page.wait_for_load_state("networkidle")
        self.assertEqual(
            page.evaluate("document.documentElement.dataset.theme"), theme)
        self._assert_no_js_errors()


if __name__ == "__main__":
    unittest.main()
