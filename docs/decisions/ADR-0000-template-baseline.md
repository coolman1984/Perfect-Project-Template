# ADR-0000 — Template baseline

| Field | Value |
|---|---|
| Status | accepted |
| Date | 2026-08-17 |
| Approved by | template author |

## Problem

The supplied master plan (v7.1) is complete as law and incomplete as an
executable artifact. An agent handed an empty repository cannot perform the
mandatory 90-second start, because every command it names lives behind a
Windows-only wrapper that does not exist yet.

## Evidence

- Part 0.1 step 2 requires `PROJECT_TOOL.bat map verify`; no such file exists in
  a new project, and it cannot run on a Linux CI runner or cloud agent at all.
- Parts 31.1 and 33 define ~68 acceptance checkboxes with no storage for which
  ones passed, when, or with what evidence.
- Rule 7 forbids inventing business meaning, with no mechanism that could
  detect a violation.
- Layers 3–10 require no Windows, Excel or DRM, yet were coupled to COM such
  that none of them could be tested without all three.

## Options considered

1. **Rewrite the constitution** for executability. Rejected: it is a good
   document, the owner approved it, and rewriting destroys the review history.
2. **Leave it and write the tooling silently.** Rejected: the tooling would
   contradict the document's own instructions, and the next agent would trust
   the document.
3. **Additive amendments plus matching tooling.** Chosen.

## Proposed option

Preserve Parts 0–35 verbatim. Add Parts 36–44, each naming the Part it refines.
Implement the tooling those Parts require, in standard-library Python so it runs
anywhere.

## Lost capabilities

None. No locked component removed, no external prerequisite added, no acceptance
gate weakened. Part 20.8's Tree-sitter ranking is implemented at reduced
fidelity, which Part 37.2 rule 4 explicitly permits and documents.

## Risks

| Risk | Mitigation |
|---|---|
| The fixture adapter becomes a habitual fallback | Four machine-checked rules; release verification fails if it ships; it can never advance the protected-file gate |
| The gate ledger becomes a green board nobody earned | `pass` requires an evidence file that exists on disk |
| Amendments drift from the original | `tests/constitution/` asserts Parts 0–35 and the seventeen rules survive |

## Equivalence tests

`tests/architecture/test_architecture_gates.py` and
`tests/constitution/test_constitution_consistency.py`: locked components present,
forbidden requirements intact, external prerequisites still only Windows + Excel,
original Parts and rules preserved, environment-bound gates report BLOCKED rather
than a false pass.

## Rollback

Delete Parts 36–44 and `tools/`. Parts 0–35 are untouched, so v7.1 is recovered
exactly. Nothing in the amendments is load-bearing for the original text.

## User approval

Recorded as `pending owner review` in `docs/CONSTITUTION_CHANGELOG.md`. The
amendments are additive and weaken nothing, but the owner should read Parts
36–44 and confirm.
