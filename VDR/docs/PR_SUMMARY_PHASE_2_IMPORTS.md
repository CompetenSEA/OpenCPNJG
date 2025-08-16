# Phase 2 – Chart Importers

## What
* Added `tools/import_enc.py`, `tools/import_cm93.py` and `tools/import_geotiff.py` to ingest ENC, CM93 and GeoTIFF data.
* Registry extended with `register_mbtiles`/`register_cog` helpers and startup scan for `data/mbtiles` and `data/geotiff`.
* Optional FastAPI admin endpoints (`/admin/import/*`) gated behind `IMPORT_API_ENABLED`.
* Runbook and operator docs updated with import instructions and troubleshooting.

## Why
Enables ingestion of real chart data into the local registry so `/charts` and
`/tiles/*` can serve imported ENC, CM93 and raster datasets without external
services.

## How
Importers call system tools (`ogr2ogr`, `tippecanoe`, `gdal_translate`) when
available and fall back gracefully when missing.  Artefacts are written under
`chart-tiler/data/*` and idempotency is maintained via SHA256 checksums.

## Requirements
* GDAL (`ogr2ogr`, `gdal_translate`) and `tippecanoe` for full functionality.
* Optional CM93 adapter via `OPENCN_CM93_CLI`.

## Risks & Rollback
Import scripts skip work when tools are missing, minimising CI impact.  To
rollback, remove generated artefacts under `data/` and rescan the registry.
