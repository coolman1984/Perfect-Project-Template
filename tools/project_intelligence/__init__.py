"""Project-native repository intelligence (Constitution Part 20.8).

Structural ranking (Aider-style personalized PageRank over a dependency graph)
plus durable catalog rendering (repo-map-style), implemented locally with the
standard library only.

Two boundaries that must never be crossed:

1. **No source disclosure.** Nothing here sends file content anywhere. Optional
   AI enrichment (Part 20.11) is off by default and needs IT + data-owner
   approval for a named provider before it may ever be added.
2. **Development intelligence only.** Production code under `app/` and `web/`
   must never import this package, and application failure must never depend on
   it (Part 20.8 rule 10). `verify_architecture --source-scan` enforces this.
"""
