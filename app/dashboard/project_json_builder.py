"""Dashboard JSON adapter for the project-centric V8.1 execution model.

The web/dashboard component model stays shared. This adapter only translates a
ProjectContract and aggregated project outcome into that stable presentation
shape; it contains no department KPI formula.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.dashboard.json_builder import _chart, _display, _number


def build(
    *,
    contract: Any,
    config: dict[str, Any],
    analytics: Any,
    outcome: Any,
) -> dict[str, Any]:
    generated = datetime.now(timezone.utc).isoformat()
    meta = config.get("meta", {})
    period = "" if analytics.period is None else str(analytics.period)
    kpis = []
    for spec in config.get("kpis", []):
        metric_id = str(spec["id"])
        value = analytics.metric_values.get(metric_id)
        kpis.append({
            "id": metric_id,
            "label": str(spec.get("label", metric_id)),
            "value": _number(value),
            "display": _display(value, str(spec.get("format", "integer"))),
            "unit": str(spec.get("unit", "")),
            "period": period,
            "comparison": None,
            "direction": str(spec.get("direction", "neutral")),
            "status": "neutral",
            "evidence_ref": f"metric:{metric_id}",
            "updated_at": generated,
        })
    charts = [
        _chart(spec, analytics.chart_rows.get(str(spec["id"]), []))
        for spec in config.get("charts", [])
    ]
    return {
        "schema_version": "1.0",
        "demo_data": bool(outcome.demo_data),
        "unapproved_definitions": bool(outcome.unapproved_definitions),
        "project": {
            "id": contract.project_id,
            "version": contract.project_version,
            "template_version": contract.template_version,
        },
        # Compatibility field for the existing shared web shell while it is
        # migrated from report discovery to project discovery.
        "report": {
            "id": contract.project_id,
            "title": str(meta.get("title", contract.project_id)),
            "period": period,
            "version": contract.project_version,
        },
        "freshness": {
            "data_date": period,
            "generated_at": generated,
            "run_id": outcome.run_id,
            "is_partial": False,
        },
        "quality": {
            "status": outcome.quality_status,
            "passed": outcome.quality_counts.get("PASS", 0),
            "warnings": outcome.quality_counts.get("WARNING", 0),
            "failed": outcome.quality_counts.get("BLOCK", 0),
            "control_totals": [
                {
                    "name": control.name,
                    "source_value": float(control.source_value),
                    "database_value": float(control.database_value),
                    "difference": float(control.difference),
                }
                for control in outcome.control_totals
            ],
        },
        "filters": {
            "definitions": [
                {
                    "id": str(spec["id"]),
                    "label": str(spec.get("label", spec["id"])),
                    "type": str(spec.get("type", "multi")),
                }
                for spec in config.get("filters", [])
            ],
            "active": {},
        },
        "kpis": kpis,
        "charts": charts,
        "tables": list(config.get("tables", [])),
        "insights": list(analytics.insights),
        "actions": list(config.get("actions", [])),
        "lineage": {
            "sources": [
                {
                    "source_id": source_id,
                    "rows": source_outcome.rows_extracted,
                }
                for source_id, source_outcome in outcome.sources.items()
            ],
            "rows": analytics.lineage_rows,
            "mapping_version": str(
                config.get("lineage", {}).get("mapping_version", "1")),
            "metric_version": str(
                config.get("lineage", {}).get("metric_version", "1")),
        },
        "downloads": list(config.get("downloads", [])),
    }
