"""Honest standalone-dashboard verification.

Static checks are always available. Full release proof additionally requires a
headless-browser probe supplied by the packaging/CI environment. A static scan
is never mislabeled as proof that JavaScript, theme, RTL, print and charts ran.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Any


@dataclass
class VerificationResult:
    static_ok: bool
    browser_verified: bool
    network_requests: list[str] = field(default_factory=list)
    js_errors: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.static_ok and self.browser_verified and not self.network_requests and not self.js_errors and all(self.checks.values())


class _ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.external: list[str] = []
        self.script_sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for name in ("src", "href", "action"):
            value = values.get(name)
            if not value:
                continue
            lowered = value.strip().lower()
            if lowered.startswith(("http://", "https://", "//")):
                self.external.append(value)
        if tag == "script" and values.get("src"):
            self.script_sources.append(values["src"] or "")


def verify_static(html_path: str | Path) -> VerificationResult:
    path = Path(html_path)
    issues: list[str] = []
    if not path.is_file():
        return VerificationResult(False, False, issues=["HTML file does not exist"])
    text = path.read_text(encoding="utf-8", errors="strict")
    parser = _ReferenceParser(); parser.feed(text)
    if parser.external:
        issues.append("external references: " + ", ".join(parser.external))
    if parser.script_sources:
        issues.append("standalone HTML still has external script files: " + ", ".join(parser.script_sources))
    if 'data-standalone-report="true"' not in text:
        issues.append("standalone marker missing")
    if "window.__DASHBOARD__=" not in text:
        issues.append("embedded dashboard JSON missing")
    if "window.echarts" not in text and "echarts.init" not in text:
        issues.append("embedded ECharts runtime marker missing")
    return VerificationResult(not issues, False, issues=issues)


def verify(
    html_path: str | Path,
    *,
    browser_probe: Callable[[Path], dict[str, Any]] | None = None,
) -> VerificationResult:
    """Verify static self-containment plus an injected real-browser probe.

    `browser_probe` must open the local file with outbound network blocked and
    return `network_requests`, `js_errors`, and boolean `checks` (for example
    kpis, charts, theme, rtl, print). Without that probe the result is honest:
    static checks may pass, but `passed` remains False.
    """
    result = verify_static(html_path)
    if not result.static_ok or browser_probe is None:
        if browser_probe is None:
            result.issues.append("headless-browser proof not supplied")
        return result
    evidence = browser_probe(Path(html_path))
    result.browser_verified = True
    result.network_requests = [str(x) for x in evidence.get("network_requests", [])]
    result.js_errors = [str(x) for x in evidence.get("js_errors", [])]
    result.checks = {str(k): bool(v) for k, v in evidence.get("checks", {}).items()}
    if result.network_requests: result.issues.append("unexpected network request(s) observed")
    if result.js_errors: result.issues.append("JavaScript error(s) observed")
    if result.checks and not all(result.checks.values()): result.issues.append("one or more browser checks failed")
    return result
