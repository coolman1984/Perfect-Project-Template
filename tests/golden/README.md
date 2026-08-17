# Golden tests

Constitution Part 15: a small known dataset with known answers.

```text
total = 8,060 produced · 100 defects · top model = MDL-A
```

If a number changes unexpectedly, the build fails. This is what catches a broken
formula that still returns a plausible-looking result.

Mandatory rerun proofs (Part 15):

- Load the same batch twice -> identical row count and control total.
- Load day 1, then day 1+2 -> only day 2 rows added.
- Change an old value -> it appears after the next run within the lookback window.

`tests/expected/` holds the approved outputs these compare against.
