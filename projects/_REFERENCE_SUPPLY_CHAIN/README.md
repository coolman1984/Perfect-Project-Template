# Supply Chain multi-source reference

This is the **project-contract reference** required by the V8.1 deep audit. It proves the project model can describe three independent source roles with different grains, keys, quality controls and history strategies, plus approved relationships and presentation configuration.

It is intentionally labelled **CONTRACT PROVEN, EXECUTION NOT YET PROVEN**. The next master-core slice must execute these three fixtures through the shared source/history/quality engine and then run cross-source SQL. Until that golden test exists, Part 36 must not call Reference B executable.

Sources:

- `orders` — transaction/upsert
- `inventory` — snapshot
- `item_master` — master/upsert

This reference exists to prevent the engine from drifting back to a single-workbook/single-history-mode design.
