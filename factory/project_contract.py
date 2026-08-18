"""Project-centric multi-source contract for employee adaptations."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib
from typing import Any

ALLOWED_LOAD_MODES = {"append", "upsert", "snapshot", "replace_period"}
ALLOWED_DELETION_RULES = {"ignore", "mark_inactive", "soft_delete"}
ALLOWED_CARDINALITIES = {"one_to_one", "one_to_many", "many_to_one", "many_to_many"}
ALLOWED_JOIN_TYPES = {"inner", "left", "full"}
ALLOWED_TYPES = {
    "VARCHAR", "DATE", "INTEGER", "BIGINT", "BOOLEAN",
    "DECIMAL(18,4)", "DECIMAL(18,2)",
}
ID = re.compile(r"^[a-z][a-z0-9_]*$")


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
    non_negative_columns: tuple[str, ...]
    column_types: dict[str, str]

    @property
    def business_columns(self) -> tuple[str, ...]:
        return tuple(self.column_types)


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
    require_match: bool


@dataclass(frozen=True)
class ProjectContract:
    project_id: str
    project_version: int
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


def _validate_identifier(value: str, *, label: str) -> str:
    if not ID.fullmatch(value):
        raise ProjectContractError(
            f"{label} must be lower_snake_case starting with a letter: {value!r}")
    return value


def discover_project_directories(projects_root: str | Path) -> dict[str, Path]:
    """Return canonical project_id -> directory without trusting folder names.

    Reference folders may deliberately start with an underscore while their
    project_id remains a normal stable identifier. The API and AI work with the
    project_id from `project.toml`, never a guessed folder name.
    """
    root = Path(projects_root)
    result: dict[str, Path] = {}
    if not root.exists():
        return result
    for directory in sorted(root.iterdir()):
        config = directory / "project.toml"
        if not directory.is_dir() or not config.is_file():
            continue
        try:
            document = tomllib.loads(config.read_text("utf-8"))
            project_id = _validate_identifier(
                str(document.get("project_id", "")).strip(), label="project_id")
        except (OSError, tomllib.TOMLDecodeError, ProjectContractError):
            continue
        if project_id in result:
            raise ProjectContractError(
                f"duplicate project_id {project_id!r} in "
                f"{result[project_id]} and {directory}")
        result[project_id] = directory
    return result


def find_project_directory(projects_root: str | Path, project_id: str) -> Path:
    project_id = _validate_identifier(project_id, label="project_id")
    discovered = discover_project_directories(projects_root)
    if project_id not in discovered:
        raise ProjectContractError(f"unknown project_id={project_id}")
    return discovered[project_id]


def load_project(directory: str | Path) -> ProjectContract:
    root = Path(directory)
    project = _load(root / "project.toml")
    sources_doc = _load(root / "sources.toml")
    relationships_doc = _load(root / "relationships.toml")

    project_id = _validate_identifier(
        str(project.get("project_id", "")).strip(), label="project_id")
    project_version = int(project.get("project_version", 1))
    template = project.get("template", {})
    if not template.get("template_id") or not template.get("template_version"):
        raise ProjectContractError("project template lineage is required")

    sources: list[SourceSpec] = []
    seen: set[str] = set()
    for raw in sources_doc.get("sources", []):
        source_id = _validate_identifier(
            str(raw.get("source_id", "")).strip(), label="source_id")
        if source_id in seen:
            raise ProjectContractError(f"source_id must be unique: {source_id!r}")
        seen.add(source_id)
        history = raw.get("history", {})
        quality = raw.get("quality", {})
        match = raw.get("match", {})
        discovery = raw.get("discovery", {})
        mode = str(history.get("mode", ""))
        deletion = str(history.get("deletion_rule", ""))
        key = tuple(str(x) for x in raw.get("business_key", []))
        column_types = {
            _validate_identifier(str(name), label=f"{source_id} column"): str(kind).upper()
            for name, kind in raw.get("column_types", {}).items()
        }
        if mode not in ALLOWED_LOAD_MODES:
            raise ProjectContractError(f"{source_id}: invalid history mode {mode!r}")
        if deletion not in ALLOWED_DELETION_RULES:
            raise ProjectContractError(
                f"{source_id}: invalid deletion rule {deletion!r}")
        if not key:
            raise ProjectContractError(
                f"{source_id}: business_key is required per source")
        if not column_types:
            raise ProjectContractError(
                f"{source_id}: column_types are required so clean/history types "
                "are explicit rather than inferred from one sample file")
        invalid_types = {
            name: kind for name, kind in column_types.items()
            if kind not in ALLOWED_TYPES
        }
        if invalid_types:
            raise ProjectContractError(
                f"{source_id}: unsupported column types {invalid_types}")
        required = tuple(str(x) for x in quality.get("required_columns", []))
        controls = tuple(str(x) for x in quality.get("control_totals", []))
        non_negative = tuple(
            str(x) for x in quality.get("non_negative_columns", []))
        referenced = set(required) | set(key) | set(controls) | set(non_negative)
        if raw.get("event_date"):
            referenced.add(str(raw["event_date"]))
        missing_types = referenced - set(column_types)
        if missing_types:
            raise ProjectContractError(
                f"{source_id}: no column type declared for {sorted(missing_types)}")
        for column in controls:
            if not column_types[column].startswith(("DECIMAL", "INTEGER", "BIGINT")):
                raise ProjectContractError(
                    f"{source_id}: control total {column!r} must be numeric")
        patterns = tuple(str(x) for x in match.get("file_patterns", []))
        if not patterns:
            raise ProjectContractError(
                f"{source_id}: at least one file pattern is required")
        sheet = str(discovery.get("sheet", "")).strip()
        if not sheet:
            raise ProjectContractError(
                f"{source_id}: sheet discovery rule is required")
        sources.append(SourceSpec(
            source_id=source_id,
            role=str(raw.get("role", "other")),
            required=bool(raw.get("required", True)),
            file_patterns=patterns,
            sheet=sheet,
            grain=str(raw.get("grain", "PENDING_APPROVAL")),
            business_key=key,
            event_date=(str(raw["event_date"])
                        if raw.get("event_date") else None),
            load_mode=mode,
            lookback_days=int(history.get("lookback_days", 0)),
            deletion_rule=deletion,
            required_columns=required,
            control_totals=controls,
            non_negative_columns=non_negative,
            column_types=column_types,
        ))
    if not sources:
        raise ProjectContractError("a project needs at least one source")

    relationships: list[RelationshipSpec] = []
    relationship_ids: set[str] = set()
    for raw in relationships_doc.get("relationships", []):
        relationship_id = _validate_identifier(
            str(raw.get("relationship_id", "")).strip(),
            label="relationship_id")
        if relationship_id in relationship_ids:
            raise ProjectContractError(
                f"relationship_id must be unique: {relationship_id!r}")
        relationship_ids.add(relationship_id)
        left = str(raw.get("left_source", ""))
        right = str(raw.get("right_source", ""))
        if left not in seen or right not in seen:
            raise ProjectContractError(
                f"relationship references unknown source: {left!r} -> {right!r}")
        left_keys = tuple(str(x) for x in raw.get("left_keys", []))
        right_keys = tuple(str(x) for x in raw.get("right_keys", []))
        if not left_keys or len(left_keys) != len(right_keys):
            raise ProjectContractError(
                "relationship key lists must be non-empty and the same length")
        left_source = next(s for s in sources if s.source_id == left)
        right_source = next(s for s in sources if s.source_id == right)
        if set(left_keys) - set(left_source.column_types):
            raise ProjectContractError(
                f"{relationship_id}: unknown left relationship key")
        if set(right_keys) - set(right_source.column_types):
            raise ProjectContractError(
                f"{relationship_id}: unknown right relationship key")
        cardinality = str(raw.get("cardinality", ""))
        join_type = str(raw.get("join_type", ""))
        if cardinality not in ALLOWED_CARDINALITIES:
            raise ProjectContractError(
                f"invalid relationship cardinality: {cardinality!r}")
        if join_type not in ALLOWED_JOIN_TYPES:
            raise ProjectContractError(
                f"invalid relationship join type: {join_type!r}")
        relationships.append(RelationshipSpec(
            relationship_id=relationship_id,
            left_source=left,
            right_source=right,
            left_keys=left_keys,
            right_keys=right_keys,
            cardinality=cardinality,
            join_type=join_type,
            approval_state=str(raw.get("approval_state", "UNKNOWN")),
            require_match=bool(raw.get("require_match", False)),
        ))

    return ProjectContract(
        project_id=project_id,
        project_version=project_version,
        template_id=str(template["template_id"]),
        template_version=str(template["template_version"]),
        sources=tuple(sources),
        relationships=tuple(relationships),
        directory=root,
    )
