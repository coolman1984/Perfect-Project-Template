"""Restricted YAML reader/writer for the gate ledger (Constitution Part 38).

Part 37.2 rule 1 forbids third-party imports in the portable tool tier, so we
cannot use PyYAML. We do not need to: `acceptance/gates.yaml` has exactly one
shape, a list of flat string-valued mappings, and this module handles that
subset and nothing else.

Supported::

    # comment
    - id: GATE_X
      title: Some text
      severity: block
      notes: "quoted: with colon"

Deliberately unsupported: nested mappings, lists of lists, anchors, multi-line
scalars, multiple documents. A file that uses them raises MiniYamlError rather
than being silently misread — a parser that guesses is worse than one that stops.
"""

from __future__ import annotations


class MiniYamlError(ValueError):
    """The ledger uses YAML we intentionally do not support."""


def _unquote(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def load_records(text: str) -> list[dict[str, str]]:
    """Parse a list of flat mappings. Returns [] for an empty document."""
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith("- "):
            if indent != 0:
                raise MiniYamlError(f"line {lineno}: nested lists are not supported")
            current = {}
            records.append(current)
            stripped = stripped[2:]
        elif current is None:
            raise MiniYamlError(f"line {lineno}: content before the first '- ' record")
        elif indent == 0:
            raise MiniYamlError(f"line {lineno}: top-level key outside a record")

        if ":" not in stripped:
            raise MiniYamlError(f"line {lineno}: expected 'key: value', got {stripped!r}")

        key, _, value = stripped.partition(":")
        key = key.strip()
        if not key:
            raise MiniYamlError(f"line {lineno}: empty key")
        current[key] = _unquote(value)

    return records


_NEEDS_QUOTING = (":", "#", "'", '"')


def _emit(value: str) -> str:
    text = "" if value is None else str(value)
    if text == "":
        return '""'
    if any(ch in text for ch in _NEEDS_QUOTING) or text != text.strip():
        return '"' + text.replace('"', '\\"') + '"'
    return text


def dump_records(records: list[dict[str, str]], header: str = "") -> str:
    """Render records back to the same restricted subset, key order preserved."""
    out: list[str] = []
    if header:
        out.extend(f"# {line}" if line else "#" for line in header.splitlines())
        out.append("")
    for record in records:
        first = True
        for key, value in record.items():
            prefix = "- " if first else "  "
            out.append(f"{prefix}{key}: {_emit(value)}")
            first = False
        out.append("")
    return "\n".join(out).rstrip() + "\n"
