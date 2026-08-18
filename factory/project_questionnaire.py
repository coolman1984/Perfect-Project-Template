"""Plain-language business interview for a multi-source employee project.

This is the V8.1 normal path. It asks business meaning. It deliberately does
not ask the employee to design storage/security/database/API/runtime choices.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class BusinessQuestion:
    id:str; prompt:str; why:str

PROJECT_QUESTIONS=(
    BusinessQuestion("purpose","What work are you trying to automate?","Keeps the automation tied to a real business job and decision."),
    BusinessQuestion("files","Add every Excel file or workbook you use for this job.","The system must understand all source roles before it builds relationships or totals."),
    BusinessQuestion("source_meanings","For each file, what business information does it contain?","Orders, inventory, master data and targets behave differently even when columns look similar."),
    BusinessQuestion("row_meanings","For each source, what does ONE ROW mean?","Each source needs its own record meaning and history behavior."),
    BusinessQuestion("record_identity","For each source, which values identify the same business record?","This prevents duplicate history and lets corrections update the right record."),
    BusinessQuestion("corrections","For each source, can earlier records change or does each file replace a current picture?","Different source roles may use different update strategies."),
    BusinessQuestion("trusted_totals","Which totals do you already use to prove each important source/report is correct?","The engine reconciles trusted controls before publishing numbers."),
    BusinessQuestion("relationships","How are the sources related in the real business?","The engine must never guess a join because two files happen to share a column name."),
    BusinessQuestion("conflicts","If two sources disagree, which source is authoritative for that business fact?","Prevents silent source-precedence guesses."),
    BusinessQuestion("decision","What decision should the dashboard help you make?","Only useful KPIs/charts should survive."),
    BusinessQuestion("exceptions","What conditions need attention or action?","Makes warnings and insights operational rather than decorative."),
    BusinessQuestion("owner","Who owns and approves the business meaning?","Business truth needs a named human owner."),
)

FORBIDDEN_EMPLOYEE_ARCHITECTURE_WORDS=("duckdb","parquet","fastapi","uvicorn","port","service","firewall","retention policy","external ai policy","database engine")

def validate_plain_language_questions()->list[str]:
    problems=[]
    for question in PROJECT_QUESTIONS:
        lower=question.prompt.lower()
        for word in FORBIDDEN_EMPLOYEE_ARCHITECTURE_WORDS:
            if word in lower: problems.append(f"{question.id}: exposes technical/security architecture term {word!r}")
    return problems
