"""Project-centric multi-source contract for employee adaptations.

A project is the adaptation unit. Sources/entities/rules belong to the project;
reports and dashboards are outputs of that project, not the container for its
data architecture.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any

ALLOWED_LOAD_MODES = {"append", "upsert", "snapshot", "replace_period"}
ALLOWED_DELETION_RULES = {"ignore", "mark_inactive", "soft_delete"}
ALLOWED_CARDINALITIES = {"one_to_one", "one_to_many", "many_to_one", "many_to_many"}
ALLOWED_JOIN_TYPES = {"inner", "left", "full"}


class ProjectContractError(ValueError):
    pass


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    role: str
    required: bool
    file_patterns: tuple[str, ...]
    sheet: str
    grain: str
    business_key: tuple[str, ...]
    event_date: str | None
    load_mode: str
    lookback_days: int
    deletion_rule: str
    required_columns: tuple[str, ...]
    control_totals: tuple[str, ...]


@dataclass(frozen=True)
class RelationshipSpec:
    relationship_id: str
    left_source: str
    right_source: str
    left_keys: tuple[str, ...]
    right_keys: tuple[str, ...]
    cardinality: str
    join_type: str
    approval_state: str


@dataclass(frozen=True)
class ProjectContract:
    project_id: str
    template_id: str
    template_version: str
    sources: tuple[SourceSpec, ...]
    relationships: tuple[RelationshipSpec, ...]
    directory: Path

    @property
    def source_ids(self) -> set[str]:
        return {source.source_id for source in self.sources}

    def source(self, source_id: str) -> SourceSpec:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        raise KeyError(source_id)


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ProjectContractError(f"missing required project contract: {path.name}")
    return tomllib.loads(path.read_text("utf-8"))


def load_project(directory: str | Path) -> ProjectContract:
    root = Path(directory)
    project = _load(root / "project.toml")
    sources_doc = _load(root / "sources.toml")
    relationships_doc = _load(root / "relationships.toml")

    project_id = str(project.get("project_id", "")).strip()
    template = project.get("template", {})
    if not project_id:
        raise ProjectContractError("project_id is required")
    if not template.get("template_id") or not template.get("template_version"):
        raise ProjectContractError("project template lineage is required")

    sources: list[SourceSpec] = []
    seen: set[str] = set()
    for raw in sources_doc.get("sources", []):
        source_id = str(raw.get("source_id", "")).strip()
        if not source_id or source_id in seen:
            raise ProjectContractError(f"source_id must be non-empty and unique: {source_id!r}")
        seen.add(source_id)
        history = raw.get("history", {})
        quality = raw.get("quality", {})
        match = raw.get("match", {})
        discovery = raw.get("discovery", {})
        mode = str(history.get("mode", ""))
        deletion = str(history.get("deletion_rule", ""))
        key = tuple(str(x) for x in raw.get("business_key", []))
        if mode not in ALLOWED_LOAD_MODES:
            raise ProjectContractError(f"{source_id}: invalid history mode {mode!r}")
        if deletion not in ALLOWED_DELETION_RULES:
            raise ProjectContractError(f"{source_id}: invalid deletion rule {deletion!r}")
        if not key:
            raise ProjectContractError(f"{source_id}: business_key is required per source")
        patterns = tuple(str(x) for x in match.get("file_patterns", []))
        if not patterns:
            raise ProjectContractError(f"{source_id}: at least one file pattern is required")
        sheet = str(discovery.get("sheet", "")).strip()
        if not sheet:
            raise ProjectContractError(f"{source_id}: sheet discovery rule is required")
        sources.append(SourceSpec(
            source_id=source_id,
            role=str(raw.get("role", "other")),
            required=bool(raw.get("required", True)),
            file_patterns=patterns,
            sheet=sheet,
            grain=str(raw.get("grain", "PENDING_APPROVAL")),
            business_key=key,
            event_date=(str(raw["event_date"]) if raw.get("event_date") else None),
            load_mode=mode,
            lookback_days=int(history.get("lookback_days", 0)),
            deletion_rule=deletion,
            required_columns=tuple(str(x) for x in quality.get("required_columns", [])),
            control_totals=tuple(str(x) for x in quality.get("control_totals", [])),
        ))
    if not sources:
        raise ProjectContractError("a project needs at least one source")

    relationships: list[RelationshipSpec] = []
    for raw in relationships_doc.get("relationships", []):
        left = str(raw.get("left_source", "")); right = str(raw.get("right_source", ""))
        if left not in seen or right not in seen:
            raise ProjectContractError(f"relationship references unknown source: {left!r} -> {right!r}")
        left_keys = tuple(str(x) for x in raw.get("left_keys", [])); right_keys = tuple(str(x) for x in raw.get("right_keys", []))
        if not left_keys or len(left_keys) != len(right_keys):
            raise ProjectContractError("relationship key lists must be non-empty and the same length")
        cardinality = str(raw.get("cardinality", "")); join_type = str(raw.get("join_type", ""))
        if cardinality not in ALLOWED_CARDINALITIES:
            raise ProjectContractError(f"invalid relationship cardinality: {cardinality!r}")
        if join_type not in ALLOWED_JOIN_TYPES:
            raise ProjectContractError(f"invalid relationship join type: {join_type!r}")
        relationships.append(RelationshipSpec(
            relationship_id=str(raw.get("relationship_id", "")), left_source=left, right_source=right,
            left_keys=left_keys, right_keys=right_keys, cardinality=cardinality, join_type=join_type,
            approval_state=str(raw.get("approval_state", "UNKNOWN")),
        ))

    return ProjectContract(
        project_id=project_id,
        template_id=str(template["template_id"]),
        template_version=str(template["template_version"]),
        sources=tuple(sources), relationships=tuple(relationships), directory=root,
    )
