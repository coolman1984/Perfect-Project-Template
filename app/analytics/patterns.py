"""Reusable evidence-backed analytical patterns.

Business formulas stay in report SQL. This module only turns approved SQL
results into common evidence objects that many departments reuse: period
movement and largest-contributor signals. It never invents a business rule.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _float(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


def _index(spec: dict[str, Any], name: str, default: int) -> int:
    return int(spec.get(name, default))


def build_insight(spec: dict[str, Any], rows: list[tuple]) -> dict[str, Any] | None:
    """Build one reusable insight from a named SQL result."""
    if not rows:
        return None
    kind = str(spec.get("type", "")).strip()
    if kind == "period_change_value":
        return _period_change_value(spec, rows[0])
    if kind == "period_change_rate":
        return _period_change_rate(spec, rows[0])
    if kind == "top_contributor":
        return _top_contributor(spec, rows[0])
    raise ValueError(
        f"unsupported insight pattern {kind!r}; add a reusable pattern instead "
        "of hiding new business logic in the engine"
    )


def _period_change_value(spec: dict[str, Any], row: tuple) -> dict[str, Any] | None:
    current_period = row[_index(spec, "current_period_index", 0)]
    current = _decimal(row[_index(spec, "current_value_index", 1)])
    comparison_period = row[_index(spec, "comparison_period_index", 2)]
    comparison = _decimal(row[_index(spec, "comparison_value_index", 3)])
    if current is None or comparison is None or comparison_period is None:
        return None
    change = current - comparison
    percent = None if comparison == 0 else change / comparison * Decimal(100)
    label = str(spec.get("label", spec.get("metric_id", "Metric")))
    unit = str(spec.get("unit", "")).strip()
    suffix = f" {unit}" if unit else ""
    query = str(spec["query"])
    metric_id = str(spec.get("metric_id", spec.get("id", "metric")))
    return {
        "id": str(spec.get("id", "period_change")),
        "type": "period_change",
        "metric_id": metric_id,
        "current_period": str(current_period),
        "current": _float(current),
        "comparison_period": str(comparison_period),
        "comparison": _float(comparison),
        "change_absolute": _float(change),
        "change_percent": _float(percent),
        "confidence": "verified",
        "evidence_refs": [f"metric:{metric_id}", f"sql:{query}"],
        "text": f"{label} moved from {comparison}{suffix} to {current}{suffix} between {comparison_period} and {current_period}.",
    }


def _period_change_rate(spec: dict[str, Any], row: tuple) -> dict[str, Any] | None:
    current_period = row[_index(spec, "current_period_index", 0)]
    current_denominator = _decimal(row[_index(spec, "current_denominator_index", 1)])
    current_numerator = _decimal(row[_index(spec, "current_numerator_index", 2)])
    comparison_period = row[_index(spec, "comparison_period_index", 3)]
    comparison_denominator = _decimal(row[_index(spec, "comparison_denominator_index", 4)])
    comparison_numerator = _decimal(row[_index(spec, "comparison_numerator_index", 5)])
    scale = Decimal(str(spec.get("scale", 1)))
    if (current_denominator in (None, Decimal(0)) or comparison_denominator in (None, Decimal(0)) or current_numerator is None or comparison_numerator is None or comparison_period is None):
        return None
    current = current_numerator / current_denominator * scale
    comparison = comparison_numerator / comparison_denominator * scale
    change = current - comparison
    percent = None if comparison == 0 else change / comparison * Decimal(100)
    label = str(spec.get("label", spec.get("metric_id", "Rate")))
    unit = str(spec.get("unit", "")).strip()
    suffix = f" {unit}" if unit else ""
    query = str(spec["query"])
    metric_id = str(spec.get("metric_id", spec.get("id", "metric")))
    return {
        "id": str(spec.get("id", "period_change")), "type": "period_change", "metric_id": metric_id,
        "current_period": str(current_period), "current": _float(current),
        "comparison_period": str(comparison_period), "comparison": _float(comparison),
        "change_absolute": _float(change), "change_percent": _float(percent),
        "confidence": "verified", "evidence_refs": [f"metric:{metric_id}", f"sql:{query}"],
        "text": f"{label} moved from {comparison:.2f}{suffix} to {current:.2f}{suffix} between {comparison_period} and {current_period}.",
    }


def _top_contributor(spec: dict[str, Any], row: tuple) -> dict[str, Any] | None:
    dimension = row[_index(spec, "dimension_index", 0)]
    value = _decimal(row[_index(spec, "value_index", 1)])
    share = _decimal(row[_index(spec, "share_index", 2)])
    if dimension is None or value is None:
        return None
    metric_id = str(spec.get("metric_id", spec.get("id", "contribution")))
    query = str(spec["query"])
    value_label = str(spec.get("value_label", "units"))
    share_text = f" ({share:.1f}% of the total)" if share is not None else ""
    return {
        "id": str(spec.get("id", "top_contributor")), "type": "contributor",
        "metric_id": metric_id, "current": _float(value), "confidence": "verified",
        "evidence_refs": [f"metric:{metric_id}", f"sql:{query}"],
        "text": f"{dimension} is the largest contributor with {value} {value_label}{share_text}. Treat it as an investigation priority, not a confirmed cause.",
    }
