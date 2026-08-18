# CURRENT STATE

The latest proven operational truth (Constitution Part 20.2). Always read this.
Update it in the **same change set** as the code it describes (Part 21.5).

> Claims here must be supported by evidence. `map verify` fails when this file
> asserts a feature or test result the evidence does not support (Part 20.5).
> The authoritative gate status is `acceptance/gates.yaml`.

---

## Two different questions — do not conflate them

| Question | Answer | Evidence |
|---|---|---|
| **Is the template skeleton verified?** | Yes | `PROJECT_TOOL doctor` passes: map, architecture, constitution, memory, gates, report validate |
| **Has a real employee project been instantiated?** | No | `reports/line_downtime/` is a demonstration second report proving config-only reuse, not a real business automation. No production report exists. |

A healthy template passes its own structural validation while having zero real
reports configured. Do not read `doctor: PASS` as "ready to process your data" —
read it as "the factory itself is not broken."

## Status

| | |
|---|---|
| **Phase** | 2 (vertical slice) — the Golden Reference now runs end to end |
| **Application version** | 0.0.0 |
| **Constitution version** | 7.2 |
| **Reports configured** | `_REFERENCE` (Golden Reference, fixture-only) · `line_downtime` (second-report proof, prototype mode, unapproved) |
| **Gate ledger** | 17 pass · 3 conditional · 1 not_applicable · 22 open (`acceptance/gates.yaml`) |

## What works right now, with evidence

- **The Golden Reference pipeline runs completely end to end** against
  synthetic fixtures: extract → stage → quality → clean → history → archive →
  metrics → insights → dashboard JSON. 24 tests in
  `tests/golden/test_reference_pipeline.py` assert against hand-derived
  expected values in `tests/expected/reference/expected.json`, not against
  whatever the code happened to produce.
- Proven by that suite: idempotent rerun, a historical correction applied in
  place, an exact duplicate quarantined, a negative value rejected to
  quarantine, an out-of-list category loaded with a warning, a blocking
  quality failure that leaves trusted history untouched, a control-total
  difference of exactly zero, Parquet archive + rebuild reconciling.
- **The Factory**: a plain-language business questionnaire
  (`factory/questionnaire.py`) that never exposes technical vocabulary,
  translated into a technical contract, an Understanding Review, a human
  approval store with value-hash binding (`factory/approvals.py`), a
  generator that seeds new reports from the Golden Reference, and a
  `.ai/BUILD_BRIEF.md` generator. `PROJECT_TOOL factory ...` — see
  `tools/factory_tool.py`.
- **The approval boundary is adversarially tested**:
  `tests/adversarial/test_approval_bypass.py` proves an agent cannot name
  itself as approver, cannot approve the sentinel, cannot silently change a
  value after approval without voiding it, and that fixture approvals are
  rejected in production mode. The trust model is documented honestly in
  `factory/approvals.py` — this is provenance and tamper-*detection*, not
  cryptographic proof against a hostile agent with write access.
- **Second-report reuse is proven**, not asserted:
  `tests/factory/test_factory_flow.py::TestFactoryCoreBoundary::test_generating_a_report_changes_no_factory_core_file`
  fingerprints every Factory Core file before and after generating a report
  and fails if a single byte changed.
- The portable tool tier, constitution audit, gate ledger and memory
  validation from the earlier template phase, unchanged.

## What does not work yet

- **No PyInstaller release, no Windows CI job, no clean-PC gate.** Everything
  needing real Windows, Excel or a protected file remains `conditional`.
- **No web UI wizard.** The Factory today is a CLI (`PROJECT_TOOL factory`);
  the brief's "same design system as the app" wizard is not built.
- **`docs/GITHUB_GOVERNANCE.md` does not exist yet** — branch protection is
  unconfirmed and undocumented.
- The dashboard HTML builder, ECharts rendering, loopback API and story mode
  are still stubs, as before.

## Pending decisions

Unchanged from the template phase for a genuinely new project. `_REFERENCE`
and `line_downtime` resolve their own subset via fixture/wizard approval; a
real business report starts from Part 18 again.

## Known risks

| Risk | Response |
|---|---|
| A future report edits Factory Core "just this once" | `TestFactoryCoreBoundary` fails the build if it does |
| An agent approves its own proposal | `factory/approvals.py` identity check + adversarial tests; documented as detection, not prevention |
| Golden Reference numbers drift silently | `tests/expected/reference/expected.json` is hand-derived and frozen; golden tests compare against it, not against current output |

## Next safe tasks

1. Windows CI job (portable Ubuntu job stays; add a Windows runner for `.bat`,
   CRLF, loopback bind, path edge cases).
2. `docs/GITHUB_GOVERNANCE.md` — required settings, since they cannot be
   changed from this environment.
3. Wire `app/dashboard/html_builder.py` and `app/dashboard/verifier.py` to the
   pipeline's already-working JSON output.
