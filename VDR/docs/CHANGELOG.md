# Documentation Changelog

## Unreleased

- ECDIS-grade light sectors now feed both core geometry and CRC32-coded labels.
- Documented LIGHTS sector and label rules in `mvt_schema.md`.
- SQL path now emits light sector geometries in `cm93-core` and
  dictionary-coded characters in `cm93-label` for `z ≥ 12`.
- Added optional `cm93_convert` native converter and importer integration.
- Converter discovery now checks `OPENCN_CM93_CLI` before `PATH` and
  falls back to GDAL when absent. `cm93_convert` also emits a GeoPackage
  with `cm93_pts`, `cm93_ln` and `cm93_ar` tables.
- Web client sources renamed to `cm93-core` and `cm93-label` with
  mariner parameters applied via style expressions instead of URL
  parameters. Added UI toggles for label plane visibility and palette
  selection.
- Exposed Prometheus metrics for tile latency and size and added CI
  performance-gate tests enforcing latency and payload budgets.
- Build script now generates content-addressed static assets with
  `manifest.json` and `PROVENANCE.txt`.
- Added service-worker caching of sprites, glyphs and tiles with
  IndexedDB LRU eviction.
- Added vendor script and shims for ISO-8211 ingestion stub build.
- Vendored minimal GDAL CPL sources and linked ocpn_min without OGR/wx/s52.
- Probe script now scans user-supplied CM93 test cells when available.
