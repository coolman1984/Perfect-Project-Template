# Copilot entry pointer (Constitution Part 20.2)

No rules live here. They live in [`AGENTS.md`](../AGENTS.md) and
[`PROJECT_SKILL.md`](../PROJECT_SKILL.md). Forking rules across entry files is
how projects drift.

Read those two first, then run `PROJECT_TOOL doctor` and
`PROJECT_TOOL map context --task "<your task>" --budget 4000`.

Three things to know before suggesting code in this repository:

- **Trusted arithmetic lives in versioned SQL**, never in Python and never in
  browser JavaScript. Suggesting a KPI calculation in `web/*.js` is a
  contract violation (Part 1.4 rule 6).
- **Never read Excel cell by cell.** Extraction uses rectangular `Range.Value2`
  blocks with adaptive chunking (Part 7.3).
- **Never invent a business key, threshold, formula or deletion rule.** Those
  belong to a named human; write `PENDING_APPROVAL` (Part 41).
