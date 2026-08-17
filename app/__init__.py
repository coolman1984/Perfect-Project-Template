"""Application package.

Layer boundaries (Constitution Part 6). Each layer has one job, one output and
one proof. A vertical feature may touch several layers through versioned
contracts, but no layer absorbs another layer's responsibility (Part 34.2).

    1  excel/session      open workbook, read-only
    2  excel/extractor    stream of rectangular chunks
    3  data/staging       raw rows + checkpoints
    4  quality/engine     PASS / WARNING / FAIL + evidence
    5  (clean)            typed, named, deduplicated
    6  data/history       insert / update / unchanged / rejected
    7  data/archive       Parquet partitions
    8  analytics/         KPI + chart tables
    9  dashboard/json     validated dashboard package
   10  dashboard/html     one offline HTML + verification

Dependency direction (Part 24.1): configuration and contracts point inward;
business logic never leaks into the UI; production layers never depend on tests;
nothing under app/ imports tools/ (Part 20.8 rule 10).
"""

__version__ = "0.0.0"
