# Vendored browser dependencies

Production release expects a **local pinned** Apache ECharts asset here:

```text
web/vendor/echarts.min.js
web/vendor/echarts.version
```

**Vendored: Apache ECharts 6.1.0** (2026-08-19).

`echarts.min.js` is `dist/echarts.min.js` extracted unmodified from the
official npm-distributed release tarball
`https://registry.npmjs.org/echarts/-/echarts-6.1.0.tgz`. Before extraction the
downloaded tarball's SHA-1 shasum was verified byte-for-byte against the
shasum published by the npm registry for `echarts@6.1.0`
(`ae0f68590f5ebbd728d900907c27acde7c5456d1`) — a mismatch would mean the
download was tampered with or corrupted, and the file would not have been
used. The file itself opens with the intact Apache Software Foundation
license header. Its own SHA-256
(`b66b25aeb4df84e33199dc21694014d336d222cbd9deb0e5a7c14bd6aa0d0fd0`) is
recorded in `IMPLEMENTATION_BASELINE.lock.json`.

The upstream project is Apache ECharts, Apache-2.0 licensed. Re-verify the
release/checksum according to the Apache download instructions before
re-vendoring a different version, and update both `echarts.version` and the
`sha256` in `IMPLEMENTATION_BASELINE.lock.json` together.

Development may render an accessible table fallback when the asset is missing. **Release/standalone HTML must fail closed** if `echarts.min.js` is absent. Never replace this with a CDN reference. Offline means bundled dependencies, not wishful networking.
