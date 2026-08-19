# Finance Purchase Price Variance — Reference D

V10 Part 34 **Reference D**: the independent-adaptation proof. Where References
A, B and C prove the engine *runs*, this one proves the engine can absorb a new
department **without being modified**.

Four independent source roles:

| Source | Role | Required | Key | History | Why it is here |
|---|---|---|---|---|---|
| `purchases` | transaction | yes | `po_number, po_line` | `upsert` (45-day lookback) | invoice corrections restate a posted line |
| `standard_cost` | master | yes | `item_id` | `upsert` | PPV is undefined without an approved standard |
| `vendors` | master | yes | `vendor_id` | `upsert` | vendor attribution for the variance |
| `ppv_budget` | target | **no** | `period` | `replace_period` | a restated budget replaces its period wholesale |

## What this reference proves that the others do not

- **An optional source.** September may be processed before Finance approves
  its PPV budget. The absent source must warn, not block.
- **An optional relationship.** `purchases_to_ppv_budget` is
  `require_match = false`, so an unmatched period is a `WARNING` and trusted
  actuals still publish. The required relationship in the same shape
  (`purchases_to_standard_cost`) blocks — both behaviours are asserted side by
  side.
- **`replace_period` history.** No other reference exercises the fourth load
  mode. A restated August budget must replace the period, not merge into it.
- **A three-source money calculation.** PPV joins purchases, standard cost and
  vendors in one trusted statement.

## The claim, and how it is checked

Adding this department required **zero Universal Core changes** — only project
configuration, project SQL, fixtures and tests.

That is not asserted in prose. `tests/golden/test_reference_reuse_boundary.py`
classifies every Reference D file through `tools/path_scope.classify_scope`
(which reads `TEMPLATE_BASELINE.json`, the same authority the core-change guard
uses) and fails if any file is core-owned. `reuse_report.json` records the same
result as machine-readable evidence: `core_files_changed: []`.

## Trusted formula

Purchase Price Variance is defined exactly once, in
`business_rules/metrics.sql`:

```text
ppv = (actual_unit_price - standard_unit_cost) * quantity
```

Positive is unfavourable. The browser renders this number and never recomputes
it (V10 Part 14.4).

## Evidence status

**REFERENCE_PROVEN on the fixture extraction port.**

`tests/golden/test_finance_ppv_reference.py` proves hand-derived variance
figures, the optional-budget warning path, the required-relationship block,
correction-without-duplication, `replace_period` restatement, evidence-backed
insight wording and idempotent rerun.

This is **not** `ENVIRONMENT_PROVEN`. Like every other reference, it runs
through the fixture adapter. Real protected Excel/COM extraction remains a
separate environment-bound gate and fixture execution is never evidence for it
(V10 Part 37).
