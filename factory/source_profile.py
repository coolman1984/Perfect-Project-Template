"""Compact privacy-conscious profiling for unfamiliar Excel structures."""
from __future__ import annotations
from dataclasses import asdict,dataclass,field
from datetime import date,datetime
from decimal import Decimal
import json,re
from typing import Any,Iterable
_ISO_DATE=re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T].*)?$"); _INTEGER=re.compile(r"^[+-]?\d+$"); _DECIMAL=re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")
@dataclass
class ColumnProfile:
 name:str; non_null:int=0; nulls:int=0; inferred_types:dict[str,int]=field(default_factory=dict); distinct_count:int|None=0; distinct_capped:bool=False; candidate_unique_key:bool=False; samples:list[str]=field(default_factory=list)
@dataclass
class SourceProfile:
 rows:int; columns:int; column_profiles:list[ColumnProfile]; sample_values_included:bool=False
 def as_dict(self)->dict[str,Any]: return asdict(self)
 def to_json(self)->str: return json.dumps(self.as_dict(),indent=2,ensure_ascii=False)
def _kind(value:Any)->str:
 if value is None or (isinstance(value,str) and not value.strip()): return "null"
 if isinstance(value,bool): return "boolean"
 if isinstance(value,(datetime,date)): return "date"
 if isinstance(value,int) and not isinstance(value,bool): return "integer"
 if isinstance(value,(float,Decimal)): return "number"
 text=str(value).strip()
 if _ISO_DATE.match(text): return "date_like_text"
 if _INTEGER.match(text): return "integer_like_text"
 if _DECIMAL.match(text): return "number_like_text"
 return "text"
def profile_chunks(chunks:Iterable[Any],*,distinct_cap:int=10000,include_samples:bool=False,sample_limit:int=3)->SourceProfile:
 columns=[]; states={}; row_count=0
 for chunk in chunks:
  cc=[str(x) for x in chunk.column_names]
  if not columns:
   columns=cc; states={n:{"non_null":0,"nulls":0,"types":{},"distinct":set(),"capped":False,"samples":[]} for n in columns}
  elif cc!=columns: raise ValueError("schema changed between chunks; profile each schema separately instead of silently merging columns")
  for row in chunk.values:
   row_count+=1
   for i,name in enumerate(columns):
    value=row[i] if i<len(row) else None; kind=_kind(value); state=states[name]; state["types"][kind]=state["types"].get(kind,0)+1
    if kind=="null": state["nulls"]+=1; continue
    state["non_null"]+=1
    if not state["capped"]:
     state["distinct"].add(str(value))
     if len(state["distinct"])>distinct_cap: state["distinct"].clear(); state["capped"]=True
    if include_samples and len(state["samples"])<sample_limit: state["samples"].append(str(value)[:80])
 profiles=[]
 for name in columns:
  s=states[name]; distinct=None if s["capped"] else len(s["distinct"])
  profiles.append(ColumnProfile(name,s["non_null"],s["nulls"],dict(sorted(s["types"].items())),distinct,s["capped"],row_count>0 and s["nulls"]==0 and not s["capped"] and distinct==row_count,list(s["samples"])))
 return SourceProfile(row_count,len(columns),profiles,include_samples)
def compact_text(profile:SourceProfile)->str:
 lines=[f"Rows: {profile.rows}",f"Columns: {profile.columns}","","| Column | Non-null | Null | Distinct | Types | Candidate unique key |","|---|---:|---:|---:|---|---|"]
 for c in profile.column_profiles:
  distinct=">" if c.distinct_capped else str(c.distinct_count); types=", ".join(f"{n}:{v}" for n,v in c.inferred_types.items()); lines.append(f"| {c.name} | {c.non_null} | {c.nulls} | {distinct} | {types} | {'yes' if c.candidate_unique_key else 'no'} |")
 lines += ["", "Samples were explicitly enabled for this profile." if profile.sample_values_included else "Raw sample values are intentionally omitted."]
 return "\n".join(lines)+"\n"
