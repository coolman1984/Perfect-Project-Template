"""Reusable evidence-backed insight patterns.

Business formulas stay in project-owned trusted SQL (or one justified isolated
Python calculation when SQL is materially inappropriate). These helpers only
turn already-verified evidence rows into neutral, non-causal statements.
"""
from __future__ import annotations
from decimal import Decimal
from typing import Any

def _decimal(value:Any)->Decimal:return Decimal(str(value if value is not None else 0))
def period_change_value(rows:list[tuple],spec:dict[str,Any],evidence_ref:str)->dict[str,Any]|None:
    if len(rows)<2:return None
    current,prior=_decimal(rows[0][1]),_decimal(rows[1][1]);delta=current-prior;label=str(spec.get("value_label","units"));direction="increased" if delta>0 else "decreased" if delta<0 else "was unchanged"
    return {"id":spec["id"],"metric_id":spec["metric_id"],"text":f"{spec['metric_id']} {direction} by {abs(delta):,.0f} {label} versus the previous period.","evidence_ref":evidence_ref,"pattern":"period_change_value"}
def period_change_rate(rows:list[tuple],spec:dict[str,Any],evidence_ref:str)->dict[str,Any]|None:
    if len(rows)<2:return None
    current,prior=_decimal(rows[0][1]),_decimal(rows[1][1]);unit=str(spec.get("unit",""));delta=current-prior;direction="increased" if delta>0 else "decreased" if delta<0 else "was unchanged"
    return {"id":spec["id"],"metric_id":spec["metric_id"],"text":f"{spec['metric_id']} {direction} by {abs(delta):,.1f}{unit} versus the previous period.","evidence_ref":evidence_ref,"pattern":"period_change_rate"}
def top_contributor(rows:list[tuple],spec:dict[str,Any],evidence_ref:str)->dict[str,Any]|None:
    if not rows:return None
    row=rows[0];dimension=str(row[int(spec.get("dimension_index",0))]);value=_decimal(row[int(spec.get("value_index",1))]);share_index=int(spec.get("share_index",2));share=_decimal(row[share_index]) if len(row)>share_index and row[share_index] is not None else None;label=str(spec.get("value_label","units"));suffix=f" ({share:.1f}% of the total)" if share is not None else ""
    return {"id":spec["id"],"metric_id":spec["metric_id"],"text":f"{dimension} is the largest contributor at {value:,.0f} {label}{suffix}.","evidence_ref":evidence_ref,"pattern":"top_contributor"}
PATTERNS={"period_change_value":period_change_value,"period_change_rate":period_change_rate,"top_contributor":top_contributor}
