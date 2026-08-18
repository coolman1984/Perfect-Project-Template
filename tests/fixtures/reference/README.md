# Golden Reference synthetic inputs

**Synthetic data only.** No real business content, no confidential rows
(Constitution Part 30.5). Everything here is fixture-approved test data.

Three files, each demonstrating something the pipeline must handle:

| File | Demonstrates |
|---|---|
| `period_1.csv` | first load; two production days; clean data |
| `period_2.csv` | a third day, **plus** a historical correction, an exact duplicate, a rejected row, and a warning-level category |
| `period_3_bad.csv` | a **blocking** quality failure: `produced_qty` renamed to `units_made` |

## What is deliberately wrong in `period_2.csv`

| Row | Content | Expected handling |
|---|---|---|
| 3 | `ORD-1008` repeated identically | de-duplicated, counted as `EXACT_DUPLICATE`, named in the population equation |
| 4 | `ORD-1003` on 2026-08-10 with `produced_qty` 950 → 1000 | **correction** inside the 7-day lookback: updates the existing record, does not insert |
| 5 | `ORD-9999` with `produced_qty` -50 | **rejected** to quarantine as `NEGATIVE_MEASURE` |
| 6 | `ORD-1009` category `trial` | **loaded with a WARNING**: outside the approved category list |

## Known exact answers

Frozen in `tests/expected/reference/expected.json` and asserted by
`tests/golden/test_reference_pipeline.py`. They are computed from these files by
hand and by SQL, and both must agree — that is the point of a golden test.
