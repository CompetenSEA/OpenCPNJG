# Map Pipeline

## Overview
Import scripts convert ENC, CM93 and GeoTIFF sources into MBTiles or Cloud Optimised GeoTIFFs. A registry scans these artefacts and exposes datasets to a FastAPI tileserver which streams tiles to the web client.

## Components
- **server-styling** – builds S-52 derived styles and sprites served at `/style/*` and `/sprites/*`.
- **chart-tiler** – FastAPI service providing `/charts`, tile routes and admin helpers.
- **web-client** – React/MapLibre UI consuming the tile APIs.

## Data flow
1. `tools/import_enc.py`/`convert_geotiff.py` create MBTiles/COG files.
2. `registry.py` scans directories, storing records in `registry.sqlite`.
3. `/charts` summarises available datasets.
4. Tile routes serve ENC vectors (`/tiles/enc/{ds}/{z}/{x}/{y}?fmt=mvt`) and GeoTIFF rasters (`/tiles/geotiff/{id}/{z}/{x}/{y}.png`).
5. The client selects bases and applies mariner settings via `createMapAPI`.

## Setup
Stage styling assets under `server-styling/dist`. Key environment variables:
`ENC_DIR`, `MBTILES_PATH`, `MBTILES_CACHE_SIZE`, `REDIS_URL`, `REDIS_TTL`, `OSM_USE_COMMUNITY`.

## Build/Run
```bash
# GeoTIFF → COG
python VDR/chart-tiler/tools/convert_geotiff.py input.tif --out-dir VDR/chart-tiler/data/geotiff

# Registry scan
python -m VDR.chart-tiler.registry --scan VDR/chart-tiler/data

# Run tileserver
uvicorn VDR.chart-tiler.tileserver:app --reload --port 8080

# Web client tests
npm test --prefix VDR/web-client
```

## Registry/DB
```sql
CREATE TABLE IF NOT EXISTS charts (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  name TEXT NOT NULL,
  path TEXT,
  url  TEXT,
  bbox TEXT,
  minzoom INTEGER,
  maxzoom INTEGER,
  updated_at TEXT,
  tags TEXT,
  status TEXT
);
CREATE TABLE IF NOT EXISTS artifacts (
  chart_id TEXT,
  type TEXT,
  path TEXT,
  sha256 TEXT,
  created_at TEXT,
  PRIMARY KEY(chart_id, type, path)
);
CREATE INDEX IF NOT EXISTS idx_charts_kind ON charts(kind);
CREATE INDEX IF NOT EXISTS idx_charts_name ON charts(name);
CREATE INDEX IF NOT EXISTS idx_artifacts_chart ON artifacts(chart_id);
```
Pragmas: `journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`. Backup via `sqlite3 registry.sqlite ".backup registry.bak"`.

## Tile APIs
- `GET /charts` → `{ base: [..], enc: { datasets: [...] } }`
- `GET /tiles/enc/{ds}/{z}/{x}/{y}?fmt=mvt`
- `GET /tiles/geotiff/{id}/{z}/{x}/{y}.png`
- `GET /titiler/*`
- `GET /metrics`, `GET /healthz`

## Frontend hooks
`createMapAPI` exposes `setBase`, `setDataset`, `setTheme` and `setMarinerParams` to manage datasets, base layers and S-52 mariner settings.

## Testing
```bash
pytest VDR/chart-tiler/tests/test_convert_geotiff.py
pytest VDR/chart-tiler/tests/test_registry_scan.py
pytest VDR/chart-tiler/tests/test_tiles_geotiff.py
pytest -q VDR/chart-tiler/tests/test_mbtiles_stream.py
pytest -q VDR/chart-tiler/tests/test_metrics_idempotent.py
npm test --prefix VDR/web-client
```

## CI/CD
Lint and unit/web tests gate Pull Requests via the commands above.

## Troubleshooting
- Missing `ETag` or caching headers: ensure proxy strips none and Redis is reachable.
- CORS errors: verify `CORSMiddleware` is active.
- Empty tiles: confirm dataset ID and tile coordinates; `/config/datasource` lists available datasets.
- Styling issues: check assets under `server-styling/dist`.
