#!/usr/bin/env python3
"""PROJECT_TOOL — portable command surface. Standard library only."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
EXIT_PASS,EXIT_FAIL,EXIT_USAGE,EXIT_BLOCKED=0,1,2,3
MIN_PYTHON=(3,11)

def _check_python():
    if sys.version_info<MIN_PYTHON:
        print("BLOCKED: Python 3.11+ required",file=sys.stderr); raise SystemExit(EXIT_BLOCKED)

def build_parser():
    parser=argparse.ArgumentParser(prog="PROJECT_TOOL",description="Map, architecture, gates, reports, V8.1 project adaptation and baseline verification."); groups=parser.add_subparsers(dest="group",metavar="<group>")
    p=groups.add_parser("map"); c=p.add_subparsers(dest="command"); c.add_parser("doctor"); c.add_parser("verify"); r=c.add_parser("refresh"); r.add_argument("--review",action="store_true"); x=c.add_parser("context"); x.add_argument("--task",required=True); x.add_argument("--budget",type=int,default=4000); x=c.add_parser("explain"); x.add_argument("--path",required=True); x=c.add_parser("changed"); x.add_argument("--base",default="HEAD")
    p=groups.add_parser("memory"); c=p.add_subparsers(dest="command"); c.add_parser("validate"); x=c.add_parser("suggest"); x.add_argument("--task",required=True); x.add_argument("--max",type=int,default=3,dest="max_items")
    p=groups.add_parser("architecture"); c=p.add_subparsers(dest="command"); x=c.add_parser("verify"); x.add_argument("--baseline",action="store_true"); x.add_argument("--source-scan",action="store_true"); x.add_argument("--release"); x.add_argument("--simulate-clean-pc",action="store_true"); x.add_argument("--simulate-missing"); x.add_argument("--standard-user-loopback",action="store_true")
    p=groups.add_parser("constitution"); c=p.add_subparsers(dest="command"); [c.add_parser(name) for name in ("audit","cross-references","architecture-terms","commands")]
    p=groups.add_parser("gates"); c=p.add_subparsers(dest="command"); x=c.add_parser("status"); x.add_argument("--severity",choices=["block","major","minor"]); x.add_argument("--only",choices=["not_started","in_progress","pass","fail","conditional","not_applicable"]); x=c.add_parser("set"); x.add_argument("--id",required=True,dest="gate_id"); x.add_argument("--status",required=True,choices=["not_started","in_progress","pass","fail","conditional","not_applicable"]); x.add_argument("--evidence",default=""); x.add_argument("--by",default="",dest="verified_by"); x.add_argument("--reason",default="",dest="conditional_reason"); x.add_argument("--next-action",default="",dest="next_action")
    p=groups.add_parser("report"); c=p.add_subparsers(dest="command"); x=c.add_parser("new"); x.add_argument("--id",required=True,dest="report_id"); x.add_argument("--title",default=""); x=c.add_parser("validate"); x.add_argument("--id",dest="report_id",default=""); x.add_argument("--mode",default="prototype",choices=["discovery","prototype","production"])
    p=groups.add_parser("factory"); c=p.add_subparsers(dest="command"); x=c.add_parser("new"); x.add_argument("--id",required=True,dest="report_id"); x.add_argument("--title",default=""); x=c.add_parser("interview"); x.add_argument("--id",required=True,dest="report_id"); x.add_argument("--question",required=True); x.add_argument("--answer",required=True); x=c.add_parser("review"); x.add_argument("--id",required=True,dest="report_id"); x=c.add_parser("approve"); x.add_argument("--id",required=True,dest="report_id"); x.add_argument("--decision",required=True); x.add_argument("--by",required=True); x.add_argument("--method",required=True,choices=sorted({"wizard_confirmation","signed_artifact","pull_request_review","external_workflow","fixture"})); x.add_argument("--evidence",required=True); x.add_argument("--notes",default=""); x=c.add_parser("generate"); x.add_argument("--id",required=True,dest="report_id"); x.add_argument("--title",default=""); x=c.add_parser("brief"); x.add_argument("--id",required=True,dest="report_id"); x=c.add_parser("status"); x.add_argument("--id",dest="report_id",default=None); x=c.add_parser("validate"); x.add_argument("--id",dest="report_id",default=None); x=c.add_parser("reference"); x.add_argument("reference_command",choices=["verify"])
    p=groups.add_parser("template-baseline",help="Git-independent sealed Universal Core baseline"); c=p.add_subparsers(dest="command"); c.add_parser("verify"); x=c.add_parser("seal"); x.add_argument("--version",required=True)
    p=groups.add_parser("adaptation",help="V8.1 employee project-pack verification"); c=p.add_subparsers(dest="command");
    for name in ("validate","core-guard","reuse-report"):
        x=c.add_parser(name); x.add_argument("--project",required=True,dest="project_id")
    groups.add_parser("doctor")
    return parser

def _dispatch(args,parser):
    if args.group=="map": from tools import project_map; return project_map.main(args)
    if args.group=="memory": from tools import project_memory; return project_memory.main(args)
    if args.group=="architecture": from tools import verify_architecture; return verify_architecture.main(args)
    if args.group=="constitution": from tools import verify_constitution; return verify_constitution.main(args)
    if args.group=="gates": from tools import gates; return gates.main(args)
    if args.group=="report": from tools import report_tool; return report_tool.main(args)
    if args.group=="factory": from tools import factory_tool; return factory_tool.main(args)
    if args.group=="template-baseline":
        from tools import template_baseline
        return template_baseline.verify() if args.command=="verify" else template_baseline.seal(template_version=args.version)
    if args.group=="adaptation": from tools import adaptation_tool; return adaptation_tool.main(args)
    if args.group=="doctor": from tools import doctor; return doctor.main(args)
    parser.print_help(); return EXIT_USAGE

def main(argv=None):
    _check_python(); parser=build_parser(); args=parser.parse_args(argv)
    if not args.group: parser.print_help(); return EXIT_USAGE
    if args.group!="doctor" and not getattr(args,"command",None): print(f"usage error: '{args.group}' needs a command",file=sys.stderr); return EXIT_USAGE
    return _dispatch(args,parser)
if __name__=="__main__": raise SystemExit(main())
