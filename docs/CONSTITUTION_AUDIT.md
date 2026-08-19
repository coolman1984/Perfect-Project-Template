# Constitution audit

Constitution Part 34.3. Machine checks plus the semantic review that automation
cannot perform.

## Machine checks

```bash
./project_tool.sh constitution audit
```

Covers: balanced code fences and front matter · duplicate or missing Part
numbers · out-of-order Parts · broken internal Part references · downgrade
language without a forbidding context · named commands that the dispatcher does
not implement · version/changelog/amendment-index agreement.

## Latest run

| Field | Value |
|---|---|
| Date | 2026-08-19 |
| Constitution version | 7.2 |
| Parts | 45 (0–44), in order, no duplicates, no gaps |
| Cross-references | 32 distinct, all resolve |
| Downgrade phrases | 7 checked in context, 0 unguarded |
| Command groups | 7 named, 12 implemented; additive project commands are documented by their active contracts |
| Result | **PASS** |

## Semantic review (Part 34.3)

Automation cannot fully understand meaning, so this section is written by hand
after every material change.

**Confirmed contradictions found and fixed**

1. *Two canonical trees.* Part 13.1 rooted at `excel-automation/`, Part 24 at
   `excel-intelligence/`. Resolved by Part 40: Part 24 is canonical, 13.1 is a
   reading aid, and the root is `<project_slug>`.
2. *Unreachable mandatory commands.* Part 0.1 required `PROJECT_TOOL.bat map
   verify` as step 2 in repositories where it cannot exist. Resolved by Part 37's
   two-tier portable contract.
3. *Unenforceable core rule.* Rule 7 forbade inventing business meaning with no
   mechanism to detect it. Resolved by Part 41's sentinel.
4. *Technical build package shown to the final operator.* The product owner's
   later explicit direction separates the complete technical template from the
   three-entry operator ZIP. ADR-0001 changes only the delivery surface and
   removes no locked capability or acceptance requirement.

**Remaining ambiguity**

| Item | Owner | Note |
|---|---|---|
| Part 20.8 asks for Tree-sitter symbol ranking; the implementation uses stdlib AST plus path references | platform | Part 37.2 rule 4 makes this an explicit, acceptable degradation rather than a silent shortfall |
| Part 29's Process Defect contract is project-specific content inside a universal document | business owner | Left as the worked example it is; a new project ignores it |
| Part 30.7 documents the historical broad release layout | product owner | ADR-0001 and `docs/PRODUCT_GOAL.md` are the approved operator-surface override; the complete sealed release remains intact inside `Application/` |

**New rules and every section they affect**

Parts 36–44, each naming the Part it refines — see the Part 36.1 index and
`docs/CONSTITUTION_IMPROVEMENTS.md`.

ADR-0001 affects the packaging surface, kickoff prompt and operating
instructions. It does not change the extraction, data, calculation, loopback,
offline, security or acceptance architecture.

**Did architecture, acceptance, tree and prompts stay aligned?**

Yes. The amendments and ADR-0001 add no external prerequisite, remove no locked
component, and weaken no acceptance gate. Part 24's tree gained `acceptance/`,
`constitution/`, `app/excel/port.py`, `app/excel/com_adapter.py`,
`app/excel/fixture_adapter.py`, `app/errors.py`, `project_tool.sh` and
`RUN_TESTS.sh` — all additive, all catalogued in the map.

`tests/constitution/test_constitution_consistency.py` asserts that Parts 0–35
and the seventeen non-negotiable rules survive future edits.
