# Performance tests

Constitution Parts 14.1, 31.3: **measure, never invent.**

v2 of the master plan guessed performance targets. That was wrong. Fill these in
from *your* files, then set targets:

```text
Excel open time · rows/sec · best chunk size · peak RAM · peak temp disk
DuckDB settings · quality gate time · history update time · SQL sync time
JSON size · HTML size · dashboard open time
typical correction window (how far back do real corrections actually happen?)
```

Interaction budgets to verify on the approved target PC (Part 26.16), recorded
as p50/p95:

```text
warm shell visible                             <= 2.0 s
filter control acknowledges input              <= 100 ms
pre-aggregated filter -> visual update         <= 500 ms p95
server-backed filtered view                    <= 2.0 s p95 or real progress
story slide change                             <= 300 ms, no focus loss
```

If a budget cannot be met, reduce payload, pre-aggregate, virtualize, cache or
simplify the visual **before** raising the limit. Never hide slow work behind
fake animation.
