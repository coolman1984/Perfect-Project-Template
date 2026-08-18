# Supply Chain multi-source reference

This is the V8.1 **Reference B** for project-centric reuse. It has three independent source roles with different grains, keys, controls and history strategies:

- `orders` — transaction / upsert with corrections
- `inventory` — dated snapshot history
- `item_master` — master / upsert

Relationships are explicit and human-confirmed in `relationships.toml`. Cross-source calculations live once in `business_rules/metrics.sql`.

## Evidence status

**EXECUTION IMPLEMENTED — CI PROOF PENDING.**

`tests/golden/test_multisource_supply_chain.py` now exercises two periods, corrections, exact-duplicate filtering, negative-row quarantine, independent source history modes, cross-source metrics, idempotent reruns, relationship blocking and an analytics failure after history mutation begins to prove the outer multi-source transaction rolls every source back together.

Do not upgrade this wording to `REFERENCE_PROVEN` until that test passes from a fresh Linux and Windows CI checkout.
