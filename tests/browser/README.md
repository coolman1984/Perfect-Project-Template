# Browser tests

Constitution Parts 11.5, 26.10. Run against the built dashboard with Playwright
and its pinned local browser (never a downloaded one).

Must prove:

```text
opens locally · ZERO unexpected network requests · zero JavaScript errors
required KPIs exist · chart containers non-empty · filters change expected data
quality/freshness/run ID match the manifest · Arabic RTL and English both render
light/dark/print layouts work · keyboard navigation and focus work
no trusted calculation happens only in browser code
```

If verification fails, the run is FAILED and the previous dashboard stays in
place. Publication is atomic.
