"""Configuration-driven analytics for the universal Excel automation engine."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib
from app.analytics.patterns import build_insight

@dataclass(frozen=True)
class AnalyticsPackage:
    metric_values: dict[str, Any]
    chart_rows: dict[str, list[tuple]]
    insights: list[dict[str, Any]]
    period: Any = ""
    lineage_rows: int = 0

def load_dashboard_config(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"missing dashboard configuration: {target}. A report must configure presentation; the universal engine must not invent business-specific KPIs or charts.")
    return tomllib.loads(target.read_text(encoding="utf-8"))

class ConfiguredAnalytics:
    """Execute only named SQL referenced by a report's dashboard config."""
    def __init__(self, runner: Any, config: dict[str, Any], *, metrics_file: str, insights_file: str) -> None:
        self.runner = runner
        self.config = config
        self.metrics_file = metrics_file
        self.insights_file = insights_file

    def run(self) -> AnalyticsPackage:
        metrics: dict[str, Any] = {}
        for spec in self.config.get("kpis", []):
            metric_id = str(spec["id"])
            metrics[metric_id] = self.runner.scalar(self.metrics_file, str(spec.get("query", metric_id)))
        chart_rows = {str(spec["id"]): self.runner.run_named(self.metrics_file, str(spec["query"])) for spec in self.config.get("charts", [])}
        insights: list[dict[str, Any]] = []
        for spec in self.config.get("insights", []):
            built = build_insight(spec, self.runner.run_named(self.insights_file, str(spec["query"])))
            if built is not None:
                insights.append(built)
            if len(insights) >= 5:
                break
        meta = self.config.get("meta", {})
        period = ""
        if meta.get("period_query"):
            value = self.runner.scalar(self.metrics_file, str(meta["period_query"]))
            period = "" if value is None else value
        lineage_rows = 0
        lineage = self.config.get("lineage", {})
        if lineage.get("rows_query"):
            lineage_rows = int(self.runner.scalar(self.metrics_file, str(lineage["rows_query"])) or 0)
        return AnalyticsPackage(metrics, chart_rows, insights, period, lineage_rows)
