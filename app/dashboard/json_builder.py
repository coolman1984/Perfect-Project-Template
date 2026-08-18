"""Build universal dashboard JSON from report configuration and approved SQL results."""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

def _number(value: Any) -> float | None:
    return None if value is None else float(Decimal(str(value)))

def _display(value: Any, style: str) -> str:
    if value is None: return "—"
    number = Decimal(str(value))
    if style == "decimal": return f"{number:,.2f}"
    if style == "percent": return f"{number:,.1f}%"
    if style == "integer": return f"{number:,.0f}"
    return str(value)

def _summary(spec: dict[str, Any], points: list[dict[str, Any]]) -> str:
    if not points: return "No data available."
    template = str(spec.get("summary_format", "")).strip(); parts=[]
    for point in points[:50]:
        if template:
            try:
                parts.append(template.format(**point)); continue
            except (KeyError, ValueError, TypeError): pass
        text=f"{point.get('x')}: {point.get('y')}"
        if point.get("cumulative") is not None: text += f" ({point['cumulative']:.1f}% cumulative)"
        parts.append(text)
    if len(points)>50: parts.append(f"... {len(points)-50} more points")
    return "; ".join(parts)

def _chart(spec: dict[str, Any], rows: list[tuple]) -> dict[str, Any]:
    xi=int(spec.get("x_index",0)); yi=int(spec.get("y_index",1)); ci=spec.get("cumulative_index"); points=[]
    for row in rows:
        point={"x":str(row[xi]) if xi<len(row) else "", "y":_number(row[yi]) if yi<len(row) else None}
        if ci is not None:
            idx=int(ci); point["cumulative"]=_number(row[idx]) if idx<len(row) and row[idx] is not None else None
        points.append(point)
    rendered=[]
    for point in points:
        item={"x":point["x"],"y":point["y"]}
        if "cumulative" in point: item["cumulative_pct"]=point["cumulative"]
        rendered.append(item)
    return {"id":str(spec["id"]),"title":str(spec["title"]),"type":str(spec.get("type","bar")),"dimensions":[str(spec.get("dimension","category"))],"series":[{"name":str(spec.get("series_name",spec.get("title",spec["id"]))),"points":rendered}],"unit":str(spec.get("unit","")),"accessible_summary":_summary(spec,points),"evidence_ref":f"sql:{spec['query']}"}

def build(*, contract: Any, analytics: Any, outcome: Any) -> dict[str, Any]:
    config=contract.dashboard; meta=config.get("meta",{}); generated=datetime.now(timezone.utc).isoformat(); period="" if analytics.period is None else str(analytics.period); quality=outcome.quality_report
    kpis=[]
    for spec in config.get("kpis",[]):
        mid=str(spec["id"]); value=analytics.metric_values.get(mid)
        kpis.append({"id":mid,"label":str(spec.get("label",mid)),"value":_number(value),"display":_display(value,str(spec.get("format","integer"))),"unit":str(spec.get("unit","")),"period":period,"comparison":None,"direction":str(spec.get("direction","neutral")),"status":"neutral","evidence_ref":f"metric:{mid}","updated_at":generated})
    charts=[_chart(spec,analytics.chart_rows.get(str(spec["id"]),[])) for spec in config.get("charts",[])]
    filters=[{"id":str(spec["id"]),"label":str(spec.get("label",spec["id"])),"type":str(spec.get("type","multi"))} for spec in config.get("filters",[])]
    return {"schema_version":"1.0","demo_data":bool(outcome.demo_data),"unapproved_definitions":"PENDING_APPROVAL" in (contract.directory/"report.toml").read_text(encoding="utf-8"),"report":{"id":contract.report_id,"title":str(meta.get("title",contract.report_id)),"period":period,"version":contract.report["report_version"]},"freshness":{"data_date":period,"generated_at":generated,"run_id":outcome.run_id,"is_partial":False},"quality":{"status":outcome.quality_status,"passed":quality.passed if quality else 0,"warnings":quality.warnings if quality else 0,"failed":quality.failed if quality else 0,"control_totals":[{"name":c.name,"source_value":float(c.source_value),"database_value":float(c.database_value),"difference":float(c.difference)} for c in outcome.control_totals]},"filters":{"definitions":filters,"active":{}},"kpis":kpis,"charts":charts,"tables":list(config.get("tables",[])),"insights":list(analytics.insights),"actions":list(config.get("actions",[])),"lineage":{"sources":[{"rows":outcome.rows_extracted}],"rows":analytics.lineage_rows,"mapping_version":str(config.get("lineage",{}).get("mapping_version","1")),"metric_version":str(config.get("lineage",{}).get("metric_version","1"))},"downloads":list(config.get("downloads",[]))}
