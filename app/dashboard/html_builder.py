"""Build a self-contained, view-only offline report from approved dashboard JSON.

The builder never reaches a CDN. It embeds the project's pinned local ECharts
asset, CSS and JSON. If the vendor asset is absent, it fails instead of quietly
turning an offline report into an internet-dependent one.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.errors import AppError

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STYLES = REPO_ROOT / "web" / "styles.css"
DEFAULT_ECHARTS = REPO_ROOT / "web" / "vendor" / "echarts.min.js"


def _script_json(value: dict[str, Any]) -> str:
    """JSON safe inside a script element, including malicious `</script>` text."""
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _read_required(path: Path, component: str) -> str:
    if not path.is_file():
        raise AppError(
            "PACKAGE_COMPONENT_MISSING",
            support_detail=f"standalone report requires local {component}: {path}",
        )
    return path.read_text(encoding="utf-8", errors="strict")


def build(
    dashboard_json: dict[str, Any], *,
    styles_path: str | Path | None = None,
    echarts_path: str | Path | None = None,
) -> str:
    """Return one self-contained HTML document with no remote references."""
    css = _read_required(Path(styles_path) if styles_path else DEFAULT_STYLES, "stylesheet")
    echarts = _read_required(Path(echarts_path) if echarts_path else DEFAULT_ECHARTS, "ECharts asset")
    payload = _script_json(dashboard_json)
    title = str(dashboard_json.get("report", {}).get("title", "Excel Intelligence"))
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    runtime = r"""
(function () {
  'use strict';
  const pack = window.__DASHBOARD__;
  const byId = (id) => document.getElementById(id);
  byId('title').textContent = pack.report.title;
  byId('period').textContent = pack.report.period || '';
  byId('quality').textContent = pack.quality.status || '';
  byId('watermarks').textContent = [pack.demo_data ? 'DEMO DATA' : '', pack.unapproved_definitions ? 'UNAPPROVED DEFINITION' : ''].filter(Boolean).join(' · ');

  const kpis = byId('kpis');
  (pack.kpis || []).forEach((item) => {
    const card = document.createElement('article'); card.className = 'kpi-card';
    const h = document.createElement('h3'); h.textContent = item.label;
    const v = document.createElement('p'); v.className = 'kpi-value'; v.textContent = item.display == null ? '—' : item.display;
    const u = document.createElement('p'); u.className = 'kpi-unit'; u.textContent = item.unit || '';
    card.append(h, v, u); kpis.append(card);
  });

  const grid = byId('charts');
  (pack.charts || []).forEach((spec) => {
    const figure = document.createElement('figure'); figure.className = 'panel';
    const caption = document.createElement('figcaption'); caption.className = 'panel-title'; caption.textContent = spec.title;
    const canvas = document.createElement('div'); canvas.className = 'chart standalone-chart'; canvas.setAttribute('role', 'img'); canvas.setAttribute('aria-label', spec.accessible_summary || spec.title);
    figure.append(caption, canvas); grid.append(figure);
    const points = (((spec.series || [])[0] || {}).points || []);
    const series = [{ name: (((spec.series || [])[0] || {}).name || spec.title), type: spec.type === 'line' ? 'line' : 'bar', data: points.map((p) => p.y) }];
    if (spec.type === 'pareto' && points.some((p) => p.cumulative_pct !== undefined)) series.push({ name: 'Cumulative %', type: 'line', yAxisIndex: 1, data: points.map((p) => p.cumulative_pct) });
    const chart = window.echarts.init(canvas);
    chart.setOption({ tooltip:{trigger:'axis'}, legend:{show:series.length>1}, xAxis:{type:'category',data:points.map((p)=>p.x)}, yAxis:series.length>1?[{type:'value',name:spec.unit||''},{type:'value',name:'%',min:0,max:100}]:{type:'value',name:spec.unit||''}, series });
  });

  const insights = byId('insights');
  (pack.insights || []).forEach((item) => { const p = document.createElement('p'); p.textContent = item.text; insights.append(p); });
  byId('theme').addEventListener('click', () => { document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; });
})();
"""

    return f"""<!DOCTYPE html>
<html lang="en" dir="auto" data-theme="light" data-standalone-report="true">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>{safe_title}</title>
<style>{css}\n.standalone-shell{{max-width:1440px;margin:auto;padding:24px}}.standalone-chart{{min-height:340px}}@media print{{#theme{{display:none!important}}}}</style>
</head>
<body>
<main class="standalone-shell">
<header class="command-header"><div class="identity"><h1 id="title"></h1><p id="period"></p></div><div class="state-strip"><span id="quality" class="badge"></span><span id="watermarks" class="watermark"></span></div><button id="theme" type="button">Theme</button></header>
<section class="region"><div id="kpis" class="kpi-strip"></div></section>
<section class="region"><div id="charts" class="grid"></div></section>
<section class="region"><h2>What this means</h2><div id="insights"></div></section>
</main>
<script>{echarts}</script>
<script>window.__DASHBOARD__={payload};</script>
<script>{runtime}</script>
</body>
</html>"""


def build_to_file(
    dashboard_json: dict[str, Any], destination: str | Path, *,
    styles_path: str | Path | None = None, echarts_path: str | Path | None = None,
) -> Path:
    """Atomically publish HTML so a failed build never replaces last-good output."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    html = build(dashboard_json, styles_path=styles_path, echarts_path=echarts_path)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(html, encoding="utf-8", newline="\n")
    os.replace(temporary, target)
    return target
