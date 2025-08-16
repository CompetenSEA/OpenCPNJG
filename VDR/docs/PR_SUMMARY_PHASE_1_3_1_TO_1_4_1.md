# Phase 1.3/1.4 Addenda Summary

This patch series introduces the GeoTIFF conversion tool, a cached chart
registry with new FastAPI endpoints, a placeholder GeoTIFF tile service and a
MapLibre AppMap capable of switching between OSM, GeoTIFF and ENC bases. It also
documents CM93/S‑57 readiness and provides operator notes for importing charts
and refreshing the registry.

## What / Why / How

- **What** – adds a GDAL‐based GeoTIFF→COG converter, a SQLite chart registry, a
  cached GeoTIFF tile proxy and MapLibre client wiring for base/theme/mariner
  switches. Documentation covers operator workflows and CM93/S‑57 readiness.
- **Why** – enables incremental ingestion of raster charts while preserving the
  existing S‑52 portrayal and offers a simple API surface for clients.
- **How** – new tooling under `chart-tiler/tools`, registry helpers and
  `/charts` endpoints in the FastAPI server, a MapProxy‑style `tiles/geotiff/*`
  facade with Prometheus metrics, an AppMap component exposing switching APIs and
  accompanying docs.

## Risks & Rollback

- Minimal risk: tile proxy is a stub and only serves cached 1×1 tiles.
- Registry scan is idempotent but operators should back up the SQLite database.
- Rollback by restoring previous images and removing generated COG/SQLite files.

## Testing

- `pytest VDR/chart-tiler/tests/test_convert_geotiff.py`
- `pytest VDR/chart-tiler/tests/test_registry_scan.py`
- `pytest VDR/chart-tiler/tests/test_tiles_geotiff.py`
- `pytest VDR/chart-tiler/tests/test_charts_api.py`
- `npm test --prefix VDR/web-client`
