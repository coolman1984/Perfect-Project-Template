#!/usr/bin/env python3
"""Project map: freshness, machine scope, ranked context and context metrics."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from tools._common import (
    EXIT_FAIL, EXIT_PASS, EXIT_USAGE, REPO_ROOT, Report, git_available,
    git_changed_files, git_ignored, git_tracked_files, iter_source_files,
    read_text, sha256_file, utc_now,
)
from tools.path_scope import classify_scope
from tools.project_intelligence import graph as pi_graph
from tools.project_intelligence import rank as pi_rank

MANIFEST_PATH = REPO_ROOT / ".ai" / "MAP_MANIFEST.json"
MAP_PATH = REPO_ROOT / ".ai" / "PROJECT_MAP.md"
CONTEXT_PATH = REPO_ROOT / ".ai" / "CONTEXT_PACK.md"
CONTEXT_METRICS_PATH = REPO_ROOT / "workspace" / "context_metrics.json"
STATE_PATH = REPO_ROOT / ".ai" / "CURRENT_STATE.md"
GENERATED_BEGIN = "<!-- GENERATED:BEGIN file-catalog — PROJECT_TOOL map refresh owns this block -->"
GENERATED_END = "<!-- GENERATED:END file-catalog -->"
ENTRY_POINTERS = ("AGENTS.md", "CLAUDE.md", ".clinerules", ".github/copilot-instructions.md", "PROJECT_SKILL.md")
REQUIRED_AI_FILES = (".ai/READ_FIRST.md", ".ai/PROJECT_MAP.md", ".ai/CURRENT_STATE.md", ".ai/CONTRACTS.md", ".ai/LESSONS.md", ".ai/OPPORTUNITIES.md", ".ai/MEMORY.jsonl")
SELF_REFERENTIAL = {".ai/MAP_MANIFEST.json"}


def _manifest_digest(relative: Path, absolute: Path) -> str:
    key = str(relative).replace("\\", "/")
    if key != ".ai/PROJECT_MAP.md":
        return sha256_file(absolute)
    text = read_text(absolute)
    if GENERATED_BEGIN in text and GENERATED_END in text:
        start = text.index(GENERATED_BEGIN); end = text.index(GENERATED_END) + len(GENERATED_END)
        text = text[:start] + text[end:]
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest() -> dict:
    entries: dict[str, dict] = {}
    for relative in iter_source_files():
        key = str(relative).replace("\\", "/")
        if key in SELF_REFERENTIAL:
            continue
        absolute = REPO_ROOT / relative
        entries[key] = {
            "sha256": _manifest_digest(relative, absolute),
            "bytes": absolute.stat().st_size,
            "scope": classify_scope(key),
        }
    return {"schema_version": 2, "generated_at": utc_now(), "file_count": len(entries), "files": entries}


def load_manifest() -> dict | None:
    if not MANIFEST_PATH.exists(): return None
    try: return json.loads(read_text(MANIFEST_PATH))
    except json.JSONDecodeError: return None


def diff_manifest(old: dict, new: dict) -> dict[str, list[str]]:
    old_files=old.get("files",{}); new_files=new.get("files",{})
    return {
        "added": sorted(set(new_files)-set(old_files)),
        "removed": sorted(set(old_files)-set(new_files)),
        "changed": sorted(path for path in set(old_files)&set(new_files)
                          if old_files[path].get("sha256") != new_files[path].get("sha256")
                          or old_files[path].get("scope") != new_files[path].get("scope")),
    }


def _check_tracked_by_git(manifest: dict, report: Report) -> None:
    if not git_available():
        report.note("git unavailable — map freshness still works; commit-state evidence skipped")
        return
    mapped=sorted(manifest.get("files",{})); ignored=git_ignored(mapped)
    for path in sorted(ignored): report.fail(f"{path} is mapped but excluded by .gitignore")
    untracked=sorted(set(mapped)-set(git_tracked_files())-ignored)
    for path in untracked: report.warn(f"{path} is mapped but not yet tracked by git")
    if not ignored and not untracked: report.note(f"all {len(mapped)} mapped files are committed and committable")


def cmd_verify() -> int:
    report=Report("map verify")
    for pointer in ENTRY_POINTERS:
        if not (REPO_ROOT/pointer).exists(): report.fail(f"missing agent entry pointer: {pointer} (Part 20.2)")
    for required in REQUIRED_AI_FILES:
        if not (REPO_ROOT/required).exists(): report.fail(f"missing project-intelligence file: {required} (Part 20.2)")
    old=load_manifest()
    if old is None:
        report.fail("no readable .ai/MAP_MANIFEST.json — run 'PROJECT_TOOL map refresh --review'")
        return report.emit()
    new=build_manifest(); delta=diff_manifest(old,new)
    for path in delta["added"]: report.fail(f"file exists but is not in the manifest: {path} (Part 20.5)")
    for path in delta["removed"]: report.fail(f"manifest lists a file that no longer exists: {path} (Part 20.5)")
    for path in delta["changed"]: report.fail(f"file/scope changed since the manifest was refreshed: {path} (Part 20.5)")
    missing_scope=[path for path,entry in old.get("files",{}).items() if not entry.get("scope")]
    for path in missing_scope: report.fail(f"map entry has no machine path scope: {path}")
    if MAP_PATH.exists():
        text=read_text(MAP_PATH)
        if GENERATED_BEGIN not in text or GENERATED_END not in text: report.fail(".ai/PROJECT_MAP.md has no generated-block markers")
        for referenced in re.findall(r"`([\w./-]+\.(?:py|sql|toml|json|md|js|css|html))`",text):
            if "<" in referenced or referenced.endswith("/"): continue
            if not (REPO_ROOT/referenced).exists() and referenced not in ("PROJECT_SKILL.md",): report.warn(f"map references a path that does not exist: {referenced}")
    _check_tracked_by_git(new,report)
    if STATE_PATH.exists() and "PENDING_APPROVAL" in read_text(STATE_PATH): report.note("CURRENT_STATE carries unresolved approvals/policy items")
    if not any(delta.values()): report.note(f"manifest matches the working tree ({new['file_count']} files) with machine scopes")
    return report.emit()


def _refresh_map_catalog(manifest: dict) -> None:
    grouped: dict[str,list[str]]={}
    for path in sorted(manifest["files"]): grouped.setdefault(path.split("/")[0] if "/" in path else "(root)",[]).append(path)
    lines=[GENERATED_BEGIN,"",f"_Generated by `PROJECT_TOOL map refresh` at {manifest['generated_at']}. {manifest['file_count']} tracked files. Every entry also has a machine `scope` in `.ai/MAP_MANIFEST.json`._",""]
    for group in sorted(grouped):
        lines += [f"#### `{group}`",""] + [f"- `{path}`" for path in grouped[group]] + [""]
    lines.append(GENERATED_END); block="\n".join(lines)
    if MAP_PATH.exists():
        text=read_text(MAP_PATH)
        if GENERATED_BEGIN in text and GENERATED_END in text:
            start=text.index(GENERATED_BEGIN); end=text.index(GENERATED_END)+len(GENERATED_END)
            MAP_PATH.write_text(text[:start]+block+text[end:],encoding="utf-8"); return
        MAP_PATH.write_text(text.rstrip()+"\n\n"+block+"\n",encoding="utf-8"); return
    MAP_PATH.parent.mkdir(parents=True,exist_ok=True); MAP_PATH.write_text(block+"\n",encoding="utf-8")


def cmd_refresh(review: bool) -> int:
    old=load_manifest() or {"files":{}}; new=build_manifest(); delta=diff_manifest(old,new)
    print("=== map refresh ==="); print(f"  files tracked: {new['file_count']}")
    for label in ("added","removed","changed"):
        items=delta[label]
        if items:
            print(f"  {label} ({len(items)}):")
            for path in items[:40]: print(f"    - {path}")
            if len(items)>40: print(f"    ... and {len(items)-40} more")
    if review and any(delta.values()): print("\n  --review: accepting the source + scope change set above.")
    MANIFEST_PATH.parent.mkdir(parents=True,exist_ok=True); MANIFEST_PATH.write_text(json.dumps(new,indent=2,sort_keys=True)+"\n",encoding="utf-8"); _refresh_map_catalog(new)
    print(f"\n  wrote {MANIFEST_PATH.relative_to(REPO_ROOT)}"); print(f"  wrote generated catalog block in {MAP_PATH.relative_to(REPO_ROOT)}"); print("\nmap refresh: PASS"); return EXIT_PASS


def cmd_context(task: str, budget: int) -> int:
    if not 1000 <= budget <= 8000:
        print(f"usage error: --budget must be 1000-8000 (Part 20.10), got {budget}"); return EXIT_USAGE
    files=iter_source_files(); graph=pi_graph.build(REPO_ROOT,files); ranked=pi_rank.rank_files(task,files,graph,REPO_ROOT)
    selected=[]; used=0; bytes_selected=0
    for path,score,reason in ranked:
        estimate=pi_rank.estimate_tokens(REPO_ROOT/path)
        if used+estimate>budget and selected: continue
        selected.append((path,score,reason)); used+=estimate; bytes_selected+=(REPO_ROOT/path).stat().st_size
        if used>=budget: break
    generated=utc_now(); lines=["# CONTEXT PACK (generated)","",f"- **Task:** {task}",f"- **Generated:** {generated}",f"- **Budget:** {budget} tokens · **Estimated selected:** ~{used} tokens",f"- **Files selected:** {len(selected)} · **Bytes selected:** {bytes_selected}","- **Expansion count:** 0 at generation time; increment it when you open outside the routed pack.","","## Ranked files","","| # | File | Scope | Score | Why it ranked |","|---:|---|---|---:|---|"]
    for index,(path,score,reason) in enumerate(selected,1): lines.append(f"| {index} | `{path}` | {classify_scope(path)} | {score:.2f} | {reason} |")
    lines += ["","## Contracts at risk",""]
    contracts=[p for p,_,_ in selected if str(p).startswith(("contracts/","projects/","reports/"))]
    lines += [f"- `{p}`" for p in contracts] if contracts else ["- None ranked. If public shape changes, open `.ai/CONTRACTS.md`."]
    lines += ["","## Tests to run",""]; tests=[p for p,_,_ in selected if str(p).startswith("tests/")]; lines += [f"- `{p}`" for p in tests] if tests else ["- None ranked directly; run focused tests for the touched layer/project."]
    lines += ["","## Before done","","```text","PROJECT_TOOL map verify","PROJECT_TOOL architecture verify --source-scan","PROJECT_TOOL constitution audit","PROJECT_TOOL gates status","```",""]
    CONTEXT_PATH.parent.mkdir(parents=True,exist_ok=True); CONTEXT_PATH.write_text("\n".join(lines),encoding="utf-8")
    metrics={"task":task,"generated_at":generated,"estimated_tokens":used,"files_selected":len(selected),"bytes_selected":bytes_selected,"expansions":0,"provider_tokens":None}
    CONTEXT_METRICS_PATH.parent.mkdir(parents=True,exist_ok=True); CONTEXT_METRICS_PATH.write_text(json.dumps(metrics,indent=2)+"\n",encoding="utf-8")
    print(f"=== map context ===\n  task: {task}"); print(f"  ranked {len(ranked)} files, selected {len(selected)} within ~{used}/{budget} tokens ({bytes_selected} bytes)"); print(f"  wrote {CONTEXT_PATH.relative_to(REPO_ROOT)} + excluded runtime context metrics"); print("\nmap context: PASS"); return EXIT_PASS


def cmd_explain(path_arg: str) -> int:
    target=Path(path_arg); absolute=REPO_ROOT/target; report=Report(f"map explain {target}")
    if not absolute.exists(): report.fail(f"path does not exist: {target}"); return report.emit()
    files=iter_source_files(); graph=pi_graph.build(REPO_ROOT,files); key=str(target).replace("\\","/")
    print(f"=== map explain: {key} ==="); print(f"  scope: {classify_scope(key)}"); print(f"  size: {absolute.stat().st_size} bytes"); print(f"  sha256: {sha256_file(absolute)[:16]}...")
    imports=graph.get(key,set()); print(f"\n  imports / references ({len(imports)}):"); [print(f"    -> {d}") for d in sorted(imports)]
    dependants=sorted(src for src,dsts in graph.items() if key in dsts); print(f"\n  depended on by ({len(dependants)}):"); [print(f"    <- {d}") for d in dependants]
    tests=[str(p) for p in files if str(p).startswith("tests/") and target.stem in str(p)]; print(f"\n  likely tests ({len(tests)}):"); [print(f"    *  {t}") for t in tests]
    print("\nmap explain: PASS"); return EXIT_PASS


def cmd_changed(base: str) -> int:
    report=Report(f"map changed --base {base}")
    if not git_available(): report.block("git unavailable; use template-baseline verification for copied-folder core integrity"); return report.emit()
    changed=git_changed_files(base)
    if not changed: report.note(f"no tracked changes against {base}"); return report.emit()
    report.note(f"{len(changed)} changed file(s) against {base}")
    for path in changed: report.note(f"{path} -> scope={classify_scope(path)}")
    report.note("Use scope plus capability registry to select focused tests; project-owned changes must not silently alter Universal Core."); return report.emit()


def cmd_doctor() -> int:
    report=Report("map doctor"); report.note(f"repo root: {REPO_ROOT}"); report.note(f"git available: {git_available()}"); report.note(f"manifest present: {MANIFEST_PATH.exists()}"); report.note(f"source files discoverable: {len(iter_source_files())}"); report.note("machine path scope authority: TEMPLATE_BASELINE.json")
    if not iter_source_files(): report.fail("no source files found — is this repository root?")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    command=args.command
    if command=="verify": return cmd_verify()
    if command=="refresh": return cmd_refresh(review=getattr(args,"review",False))
    if command=="context": return cmd_context(args.task,args.budget)
    if command=="explain": return cmd_explain(args.path)
    if command=="changed": return cmd_changed(args.base)
    if command=="doctor": return cmd_doctor()
    print(f"usage error: unknown map command {command!r}"); return EXIT_FAIL
