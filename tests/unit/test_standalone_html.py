from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.dashboard.html_builder import build, build_to_file
from app.dashboard.verifier import verify, verify_static
from app.errors import AppError


PACK = {
    "report": {"title": "Finance <Close>", "period": "2026-08"},
    "quality": {"status": "PASS"}, "demo_data": False, "unapproved_definitions": False,
    "kpis": [{"label": "Amount", "display": "1,234", "unit": "EGP"}],
    "charts": [{"id": "trend", "title": "Trend", "type": "line", "unit": "EGP", "accessible_summary": "Aug: 1234 EGP", "series": [{"name": "Amount", "points": [{"x": "Aug", "y": 1234}]}]}],
    "insights": [{"text": "The approved value changed. </script><script>alert(1)</script>"}],
}


class TestStandaloneHtml(unittest.TestCase):
    def test_build_is_self_contained_and_escapes_script_breakout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); css = root / "styles.css"; vendor = root / "echarts.min.js"
            css.write_text("body{font-family:sans-serif}", encoding="utf-8")
            vendor.write_text("window.echarts={init:function(){return {setOption:function(){}}}};", encoding="utf-8")
            html = build(PACK, styles_path=css, echarts_path=vendor)
            self.assertIn('data-standalone-report="true"', html)
            self.assertNotIn("</script><script>alert(1)</script>", html)
            self.assertNotIn('<script src=', html)
            path = root / "report.html"; path.write_text(html, encoding="utf-8")
            static = verify_static(path); self.assertTrue(static.static_ok, static.issues)

    def test_missing_echarts_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); css = root / "styles.css"; css.write_text("body{}", encoding="utf-8")
            with self.assertRaises(AppError) as caught: build(PACK, styles_path=css, echarts_path=root / "missing.js")
            self.assertEqual(caught.exception.code, "PACKAGE_COMPONENT_MISSING")

    def test_atomic_file_build_and_honest_browser_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); css = root / "styles.css"; vendor = root / "echarts.min.js"; target = root / "out" / "report.html"
            css.write_text("body{}", encoding="utf-8"); vendor.write_text("window.echarts={init:function(){return {setOption:function(){}}}};", encoding="utf-8")
            build_to_file(PACK, target, styles_path=css, echarts_path=vendor); self.assertTrue(target.exists())
            without_browser = verify(target); self.assertFalse(without_browser.passed); self.assertFalse(without_browser.browser_verified)
            with_browser = verify(target, browser_probe=lambda _path: {"network_requests": [], "js_errors": [], "checks": {"kpis": True, "charts": True, "theme": True, "rtl": True, "print": True}})
            self.assertTrue(with_browser.passed, with_browser.issues)

    def test_static_verifier_rejects_remote_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.html"; path.write_text('<html data-standalone-report="true"><script src="https://example.invalid/x.js"></script><script>window.__DASHBOARD__={};window.echarts={};</script></html>', encoding="utf-8")  # FORBIDDEN negative test input
            result = verify_static(path); self.assertFalse(result.static_ok); self.assertTrue(any("external" in x for x in result.issues))
