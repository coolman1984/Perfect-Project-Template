"""Measurable reuse evidence without a flattering denominator."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from factory.project_contract import find_project_directory,load_project
from tools._common import REPO_ROOT
from tools.path_scope import classify_scope


def build_reuse_report(project_id: str, *, projects_root: Path) -> dict[str,Any]:
    project=load_project(find_project_directory(projects_root,project_id)); files=[p for p in project.directory.rglob("*") if p.is_file()]
    buckets={"project_config":[],"business_logic":[],"presentation":[],"project_test":[],"universal_core":[]}
    for path in files:
        relative=path.relative_to(REPO_ROOT) if REPO_ROOT in path.parents else path.relative_to(projects_root.parent)
        scope=classify_scope(relative)
        buckets.setdefault(scope,[]).append(str(relative).replace("\\","/"))
    manifest_path=project.directory/"adaptation_manifest.json"; reused=[]
    if manifest_path.exists():
        data=json.loads(manifest_path.read_text("utf-8")); reused=sorted({str(item.get("capability_id")) for item in data.get("requirements",[]) if item.get("capability_id")})
    metrics_path=REPO_ROOT/"workspace"/"context_metrics.json"; metrics={"estimated_tokens":0,"files_selected":0,"bytes_selected":0,"expansions":0,"provider_tokens":None}
    if metrics_path.exists():
        try: metrics.update(json.loads(metrics_path.read_text("utf-8")))
        except json.JSONDecodeError: pass
    return {
        "project_id":project.project_id,
        "core_files_changed":sorted(buckets.get("universal_core",[])),
        "project_config_files_changed":sorted(buckets.get("project_config",[])+buckets.get("presentation",[])),
        "business_logic_files_changed":sorted(buckets.get("business_logic",[])),
        "reused_capabilities":reused,
        "reused_tests":sorted(buckets.get("project_test",[])),
        "new_architecture_decisions":0,
        "context_proxy":{key:metrics.get(key) for key in ("estimated_tokens","files_selected","bytes_selected","expansions")},
        "provider_tokens":metrics.get("provider_tokens"),
        "note":"No reuse percentage is used as acceptance evidence. Counts/scopes/context are the primary measures."
    }
