"""Execute approved deterministic SQL statements by stable metric id.

Trusted calculations should use versioned SQL when practical because it is easy
to reconcile against DuckDB and keeps formulas in one place. The V8.1 rule is
not an absolute Python ban: an isolated, tested Python calculation is allowed
when SQL would be unsafe or materially less clear. The same trusted formula may
never exist in both places, and browser JavaScript is never the trusted source.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from app.data.database import Database
NAME_MARKER = re.compile(r"^--\s*name:\s*([a-z][a-z0-9_]*)\s*$", re.MULTILINE)
class MetricError(RuntimeError): pass
@dataclass(frozen=True)
class NamedStatement:
    name:str; sql:str
def parse_named_statements(text:str)->dict[str,NamedStatement]:
    matches=list(NAME_MARKER.finditer(text)); statements={}
    for index,match in enumerate(matches):
        start=match.end(); end=matches[index+1].start() if index+1<len(matches) else len(text); body=text[start:end].strip()
        if body: statements[match.group(1)]=NamedStatement(match.group(1),body)
    return statements
class SqlRunner:
    def __init__(self,database:Database,sql_directory:Path)->None:
        self.database=database; self.sql_directory=Path(sql_directory); self._cache={}
    def statements(self,filename:str)->dict[str,NamedStatement]:
        if filename not in self._cache:
            path=self.sql_directory/filename
            if not path.exists(): raise MetricError(f"missing approved SQL file: {path}")
            self._cache[filename]=parse_named_statements(path.read_text(encoding="utf-8"))
        return self._cache[filename]
    def run_named(self,filename:str,name:str,parameters:list[Any]|None=None)->list[tuple]:
        available=self.statements(filename)
        if name not in available: raise MetricError(f"{name!r} is not defined in {filename}; configured trusted SQL must name every requested statement")
        return self.database.query(available[name].sql,parameters)
    def run_script(self,filename:str,name:str,parameters:list[Any]|None=None)->None:
        available=self.statements(filename)
        if name not in available: raise MetricError(f"{name!r} is not defined in {filename}")
        self.database.execute(available[name].sql,parameters)
    def scalar(self,filename:str,name:str,parameters:list[Any]|None=None)->Any:
        rows=self.run_named(filename,name,parameters); return rows[0][0] if rows and rows[0] else None
def as_decimal(value:Any)->Decimal: return Decimal(str(value if value is not None else 0))
def weighted_rate_ppm(numerator:Any,denominator:Any)->Decimal|None:
    denominator_value=as_decimal(denominator)
    if denominator_value==0:return None
    return as_decimal(numerator)/denominator_value*Decimal(1_000_000)
