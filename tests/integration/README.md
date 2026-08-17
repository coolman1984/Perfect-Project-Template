# Integration tests

Constitution Part 15: layer-to-layer proof.

```text
Excel -> DuckDB · DuckDB -> history · DuckDB -> SQL staging
analytics -> JSON · JSON -> HTML
```

Use the fixture adapter (Part 44) so these run on any machine. That is the
whole reason the extraction port exists — layers 3-10 need no Windows.
