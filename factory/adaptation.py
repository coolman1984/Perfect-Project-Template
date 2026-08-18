"""Adaptation manifest, reuse indicator and Universal Core change guard."""
from __future__ import annotations
from dataclasses import asdict,dataclass,field
import json
from pathlib import Path
import re,tomllib
from typing import Any
CORE_PREFIXES=("app/","factory/","tools/","contracts/","constitution/",".github/"); CORE_FILES={"AGENTS.md","PROJECT_SKILL.md","PROJECT_TOOL.bat","project_tool.sh","IMPLEMENTATION_BASELINE.lock.json"}
class CoreChangeRequired(RuntimeError): pass
def normalize_path(path:str)->str: return path.replace("\\","/").lstrip("./")
def classify_path(path:str)->str:
 value=normalize_path(path)
 if value in CORE_FILES or value.startswith(CORE_PREFIXES): return "universal_core"
 if value.startswith("reports/"):
  if "/sql/" in value: return "business_logic"
  if value.endswith("/dashboard.toml"): return "presentation_config"
  return "project_config"
 if re.match(r"^migrations/\d+_.*\.sql$",value): return "project_data_shape"
 if value.startswith("tests/fixtures/") or value.startswith("tests/expected/"): return "project_test_data"
 if value.startswith("tests/"): return "tests"
 if value.startswith("docs/"): return "documentation"
 if value.startswith(".ai/"): return "agent_context"
 return "other"
def core_change_guard(paths:list[str],*,reason:str="")->list[str]:
 core=[normalize_path(p) for p in paths if classify_path(p)=="universal_core"]
 if core and not reason.strip(): raise CoreChangeRequired("ordinary report adaptation touched Universal Core without a reason: "+", ".join(core))
 return core
DEFAULT_REUSED_CAPABILITIES=("authorized Excel extraction adapter","chunked staging with lineage","DuckDB transaction/database layer","Parquet history archive","four-mode history engine","quality and reconciliation engine","quarantine and fail-closed behavior","versioned SQL runner","configuration-driven analytics","configuration-driven dashboard JSON","loopback API architecture","offline packaging architecture","project map and context router","acceptance gates and regression tests")
@dataclass
class AdaptationManifest:
 report_id:str; department:str="PENDING_APPROVAL"; purpose:str="PENDING_APPROVAL"; sources:list[str]=field(default_factory=list); grain:str="PENDING_APPROVAL"; business_keys:list[str]=field(default_factory=list); update_strategy:str="PENDING_APPROVAL"; kpis:list[str]=field(default_factory=list); dashboard_components:list[str]=field(default_factory=list); core_modules_reused:list[str]=field(default_factory=lambda:list(DEFAULT_REUSED_CAPABILITIES)); custom_logic_added:list[str]=field(default_factory=list)
 def as_dict(self)->dict[str,Any]: return asdict(self)
 def reuse_indicator(self)->int:
  total=len(self.core_modules_reused)+len(self.custom_logic_added); return 100 if total==0 else round(len(self.core_modules_reused)/total*100)
def manifest_from_report(report_id:str,*,reports_root:Path,department:str="PENDING_APPROVAL")->AdaptationManifest:
 d=reports_root/report_id; report=tomllib.loads((d/"report.toml").read_text("utf-8")); dashboard=tomllib.loads((d/"dashboard.toml").read_text("utf-8")) if (d/"dashboard.toml").exists() else {}; history=report.get("history",{}); excel=report.get("excel",{}); sql=sorted(str(p.relative_to(d)) for p in (d/"sql").glob("*.sql")) if (d/"sql").exists() else []
 return AdaptationManifest(report_id,department,str(report.get("output",{}).get("audience",report_id)),[f"{k}: {excel[k]}" for k in ("sheet","data_area") if excel.get(k)],"PENDING_APPROVAL",[str(x) for x in history.get("business_key",[])],str(report.get("load_mode","PENDING_APPROVAL")),[f"{s.get('id')}: {s.get('label',s.get('id'))}" for s in dashboard.get("kpis",[])],[f"{s.get('type','chart')}: {s.get('id')}" for s in dashboard.get("charts",[])],list(DEFAULT_REUSED_CAPABILITIES),sql)
def write_manifest(report_id:str,*,reports_root:Path,department:str="PENDING_APPROVAL")->AdaptationManifest:
 m=manifest_from_report(report_id,reports_root=reports_root,department=department); d=reports_root/report_id; (d/"adaptation_manifest.json").write_text(json.dumps(m.as_dict(),indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); (d/"adaptation_manifest.md").write_text(f"# Adaptation Manifest — {report_id}\n\nCapability-level reuse indicator: **{m.reuse_indicator()}%**. This is directional, not exact code math.\n\nUniversal Core reused: {len(m.core_modules_reused)} capabilities.\nCustom report SQL files: {len(m.custom_logic_added)}.\n",encoding="utf-8"); return m
