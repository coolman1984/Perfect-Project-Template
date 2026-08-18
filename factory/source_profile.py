"""Compact privacy-conscious profiling for unfamiliar Excel structures."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
import json
import re
from typing import Any, Iterable

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T].*)?$")
_INTEGER = re.compile(r"^[+-]?\d+$")
_DECIMAL = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


@dataclass
class ColumnProfile:
    name: str
    non_null: int = 0
    nulls: int = 0
    inferred_types: dict[str, int] = field(default_factory=dict)
    distinct_count: int | None = 0
    distinct_capped: bool = False
    candidate_unique_key: bool = False
    samples: list[str] = field(default_factory=list)


@dataclass
class SourceProfile:
    rows: int
    columns: int
    column_profiles: list[ColumnProfile]
    sample_values_included: bool = False
    source_id: str = "unassigned"
    profile_mode: str = "metadata_only"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, ensure_ascii=False)


def _kind(value: Any) -> str:
    if value is None or (isinstance(value, str) and not value.strip()): return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, (datetime, date)): return "date"
    if isinstance(value, int) and not isinstance(value, bool): return "integer"
    if isinstance(value, float): return "number"
    text = str(value).strip()
    if _ISO_DATE.match(text): return "date_like_text"
    if _INTEGER.match(text): return "integer_like_text"
    if _DECIMAL.match(text): return "number_like_text"
    return "text"


def profile_chunks(chunks: Iterable[Any], *, distinct_cap: int = 10_000,
                   include_samples: bool = False, sample_limit: int = 3,
                   source_id: str = "unassigned", sample_policy_approved: bool = False) -> SourceProfile:
    """Profile chunked data without loading business rows into AI context.

    Metadata/statistics are the default. Sample values require a deliberate
    policy-approved call; merely setting include_samples is not sufficient.
    """
    if include_samples and not sample_policy_approved:
        raise PermissionError(
            "sample values are disabled by default; IT/Security policy approval is required")
    columns: list[str] = []; states: dict[str, dict[str, Any]] = {}; row_count = 0
    for chunk in chunks:
        chunk_columns = [str(x) for x in chunk.column_names]
        if not columns:
            columns = chunk_columns
            states = {name: {"non_null": 0, "nulls": 0, "types": {}, "distinct": set(), "capped": False, "samples": []} for name in columns}
        elif chunk_columns != columns:
            raise ValueError("schema changed between chunks; profile each source/schema separately instead of silently merging columns")
        for row in chunk.values:
            row_count += 1
            for index, name in enumerate(columns):
                value = row[index] if index < len(row) else None
                kind = _kind(value); state = states[name]
                state["types"][kind] = state["types"].get(kind, 0) + 1
                if kind == "null": state["nulls"] += 1; continue
                state["non_null"] += 1
                if not state["capped"]:
                    state["distinct"].add(str(value))
                    if len(state["distinct"]) > distinct_cap:
                        state["distinct"].clear(); state["capped"] = True
                if include_samples and len(state["samples"]) < sample_limit:
                    state["samples"].append(str(value)[:80])
    profiles: list[ColumnProfile] = []
    for name in columns:
        state = states[name]; distinct = None if state["capped"] else len(state["distinct"])
        profiles.append(ColumnProfile(name, state["non_null"], state["nulls"], dict(sorted(state["types"].items())), distinct, state["capped"], row_count > 0 and state["nulls"] == 0 and not state["capped"] and distinct == row_count, list(state["samples"])))
    mode = "approved_values" if include_samples else "metadata_only"
    return SourceProfile(row_count, len(columns), profiles, include_samples, source_id, mode)


def compact_text(profile: SourceProfile) -> str:
    lines = [f"Source: {profile.source_id}", f"Profile mode: {profile.profile_mode}", f"Rows: {profile.rows}", f"Columns: {profile.columns}", "", "| Column | Non-null | Null | Distinct | Types | Candidate unique key |", "|---|---:|---:|---:|---|---|"]
    for column in profile.column_profiles:
        distinct = ">cap" if column.distinct_capped else str(column.distinct_count)
        types = ", ".join(f"{name}:{count}" for name, count in column.inferred_types.items())
        lines.append(f"| {column.name} | {column.non_null} | {column.nulls} | {distinct} | {types} | {'yes' if column.candidate_unique_key else 'no'} |")
    lines += ["", "Samples were explicitly policy-approved for this profile." if profile.sample_values_included else "Raw sample values are intentionally omitted."]
    return "\n".join(lines) + "\n"
