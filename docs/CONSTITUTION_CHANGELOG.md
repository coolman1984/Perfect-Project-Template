# Constitution changelog

Required by Constitution Part 36.2. Every version change appends a row here.

```text
MINOR  additive amendment: new Part, new machine check, clarified rule
MAJOR  any change to Parts 0-35 text, any locked component change,
       any acceptance gate removed or weakened
```

An agent may author a MINOR amendment that strengthens or clarifies an existing
rule. An agent may **not** author a MAJOR change — that is a Part 0.7 deviation
requiring explicit user approval, recorded in `docs/decisions/`.

`PROJECT_TOOL constitution audit` fails when the version block, this changelog,
and the Part 36.1 amendment index disagree.

| Version | Date | Author class | Affected Parts | Approved by | Summary |
|---|---|---|---|---|---|
| 7.2 | 2026-08-17 | agent proposal (MINOR, additive) | adds 36–44; Parts 0–35 unchanged | pending owner review | Closes nine executability gaps found when turning the constitution into a reusable template: portable tool contract, machine-readable gate ledger, Phase −2 instantiation, tree/naming precedence, `PENDING_APPROVAL` sentinel, error codes and run states as data, secret-handling contract, extraction port with dev/test adapters, and changelog discipline. No locked component removed, no prerequisite added, no gate weakened. |
| 7.1 | 2026-08-17 | human owner | 0–35 | owner | Merged V3 + V4 master plans with the offline web-app, reusable-skill, project-map, token-control and continuous-learning requirements. Baseline for this template. |

## Amending safely

1. Confirm the change is MINOR by the definition above. If it touches Parts 0–35 or
   any locked component, stop and raise a Part 0.7 deviation instead.
2. Add the new Part at the end, in number order.
3. Add its row to the Part 36.1 amendment index, naming which earlier Part it refines.
4. Bump `**Version:**` in the constitution header.
5. Append a row here.
6. Run `PROJECT_TOOL constitution audit`.
7. Record the Part 34.3 semantic review in `docs/CONSTITUTION_AUDIT.md`.
