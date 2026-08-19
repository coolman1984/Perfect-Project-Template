# Supply Chain multi-source reference

This is **Reference C** for project-centric reuse (V10 Part 34). Older V8.1
wording called it "Reference B"; under the V10 letters, B is the Maintenance
downtime project (`reports/line_downtime/`) and C is this one. It has three
independent source roles with different grains, keys, controls and history
strategies:

- `orders` — transaction / upsert with corrections
- `inventory` — dated snapshot history
- `item_master` — master / upsert

Relationships are explicit and human-confirmed in `relationships.toml`. Cross-source calculations live once in `business_rules/metrics.sql`.

## Evidence status

**REFERENCE_PROVEN on the fixture extraction port.**

`tests/golden/test_multisource_supply_chain.py` exercises two periods, corrections, exact-duplicate filtering, negative-row quarantine, independent source history modes, cross-source metrics, idempotent reruns, relationship blocking, an analytics failure after history mutation begins (proving the outer multi-source transaction rolls every source back together), and per-source Parquet archive rebuild.

This is **not** `ENVIRONMENT_PROVEN`. The proof runs through the fixture adapter; real protected Excel/COM extraction is a separate environment-bound gate and fixture execution is never evidence for it (V10 Part 37).
