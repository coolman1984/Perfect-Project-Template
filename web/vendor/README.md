# Vendored browser dependencies

Production release expects a **local pinned** Apache ECharts asset here:

```text
web/vendor/echarts.min.js
web/vendor/echarts.version
```

Pinned target for this branch: **Apache ECharts 6.1.0** (released May 19, 2026).

The upstream project is Apache ECharts, Apache-2.0 licensed. Obtain the release from the official Apache/GitHub release, verify the release/checksum according to the Apache download instructions, then record the exact SHA-256 in the release dependency manifest.

Development may render an accessible table fallback when the asset is missing. **Release/standalone HTML must fail closed** if `echarts.min.js` is absent. Never replace this with a CDN reference. Offline means bundled dependencies, not wishful networking.
