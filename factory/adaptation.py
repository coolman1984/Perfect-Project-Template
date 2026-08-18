"""Adaptation evidence, measurable reuse and Universal Core change guard."""
from __future__ import annotations
from dataclasses import asdict,dataclass,field
import json,re
from pathlib import Path
from typing import Any
from tools.path_scope import classify_scope,load_baseline,normalize_path
class CoreChangeRequired(RuntimeError): pass

def classify_path(path:str)->str:
    value=normalize_path(path)
    # Legacy report compatibility needs finer classification than the broad
    # baseline legacy_report_config scope.
    if value.startswith("reports/"):
        if "/sql/" in value: return "business_logic"
        if value.endswith("/dashboard.toml"): return "presentation_config"
        return "project_config"
    if re.match(r"^migrations/\d+_.*\.sql$",value): return "project_data_shape"
    scope=classify_scope(value)
    return "presentation_config" if scope=="presentation" else scope if scope!="unknown" else "other"

def core_change_guard(paths:list[str],*,reason:str="")->list[str]:
    core=[normalize_path(p) for p in paths if classify_path(p) in {"universal_core","tooling"}]
    if core and not reason.strip(): raise CoreChangeRequired("employee adaptation touched core-owned files without master-core justification: "+", ".join(core))
    return core
@dataclass
class RequirementClassification:
    requirement:str; classification:str; capability_id:str|None=None; justification:str=""
@dataclass
class AdaptationManifest:
    project_id:str; template:dict[str,Any]; sources:list[str]=field(default_factory=list); relationships:list[str]=field(default_factory=list); requirements:list[RequirementClassification]=field(default_factory=list); core_changes:list[str]=field(default_factory=list); verification:dict[str,Any]=field(default_factory=dict); context_metrics:dict[str,Any]=field(default_factory=dict); schema_version:int=1
    def as_dict(self): return asdict(self)
def manifest_from_project(project_id:str,*,projects_root:Path)->AdaptationManifest:
    from factory.project_contract import find_project_directory,load_project
    # A project directory name is not required to equal its project_id
    # (projects/_REFERENCE_SUPPLY_CHAIN declares reference_supply_chain).
    project=load_project(find_project_directory(projects_root,project_id)); baseline=load_baseline()
    return AdaptationManifest(project.project_id,{"template_id":project.template_id,"template_version":project.template_version,"sealed":bool(baseline.get("sealed"))},[s.source_id for s in project.sources],[r.relationship_id for r in project.relationships])
def write_project_manifest(project_id:str,*,projects_root:Path)->AdaptationManifest:
    from factory.project_contract import find_project_directory
    manifest=manifest_from_project(project_id,projects_root=projects_root); (find_project_directory(projects_root,project_id)/"adaptation_manifest.json").write_text(json.dumps(manifest.as_dict(),indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); return manifest
DEFAULT_REUSED_CAPABILITIES=("excel.authorized_com","data.staging_lineage","history.standard_modes","quality.reconciliation","analytics.sql_metrics","dashboard.configured","runtime.loopback","ai.map_context")
@dataclass
class LegacyReportManifest:
    report_id:str; department:str="PENDING_APPROVAL"; purpose:str="PENDING_APPROVAL"; sources:list[str]=field(default_factory=list); grain:str="PENDING_APPROVAL"; business_keys:list[str]=field(default_factory=list); update_strategy:str="PENDING_APPROVAL"; kpis:list[str]=field(default_factory=list); dashboard_components:list[str]=field(default_factory=list); core_modules_reused:list[str]=field(default_factory=lambda:list(DEFAULT_REUSED_CAPABILITIES)); custom_logic_added:list[str]=field(default_factory=list)
    def as_dict(self): return asdict(self)
    def reuse_indicator(self):
        total=len(self.core_modules_reused)+len(self.custom_logic_added); return 100 if total==0 else round(len(self.core_modules_reused)/total*100)
def manifest_from_report(report_id:str,*,reports_root:Path,department:str="PENDING_APPROVAL")->LegacyReportManifest:
    import tomllib
    directory=reports_root/report_id; report=tomllib.loads((directory/"report.toml").read_text("utf-8")); dashboard=tomllib.loads((directory/"dashboard.toml").read_text("utf-8")) if (directory/"dashboard.toml").exists() else {}; history=report.get("history",{}); excel=report.get("excel",{}); sql=sorted(str(p.relative_to(directory)) for p in (directory/"sql").glob("*.sql")) if (directory/"sql").exists() else []
    return LegacyReportManifest(report_id,department,str(report.get("output",{}).get("audience",report_id)),[f"{k}: {excel[k]}" for k in ("sheet","data_area") if excel.get(k)],"PENDING_APPROVAL",[str(x) for x in history.get("business_key",[])],str(report.get("load_mode","PENDING_APPROVAL")),[f"{i.get('id')}: {i.get('label',i.get('id'))}" for i in dashboard.get("kpis",[])],[f"{i.get('type','chart')}: {i.get('id')}" for i in dashboard.get("charts",[])],list(DEFAULT_REUSED_CAPABILITIES),sql)
def write_manifest(report_id:str,*,reports_root:Path,department:str="PENDING_APPROVAL")->LegacyReportManifest:
    manifest=manifest_from_report(report_id,reports_root=reports_root,department=department); d=reports_root/report_id; (d/"adaptation_manifest.json").write_text(json.dumps(manifest.as_dict(),indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); (d/"adaptation_manifest.md").write_text(f"# Legacy Adaptation Manifest — {report_id}\n\nCompatibility artifact. New work uses projects/<project_id>/.\n",encoding="utf-8"); return manifest
