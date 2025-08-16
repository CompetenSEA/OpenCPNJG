# Map pipeline

## Overview
Import charts, register them, serve tiles and consume them in the web client. ENC, CM93 and GeoTIFF sources are ingested to MBTiles/COG, discovered by the registry and exposed through HTTP tile APIs used by MapLibre.

## Components
- **server-styling** – builds S-52 styles and sprites.
- **chart-tiler** – FastAPI tile server and registry tools.
- **web-client** – React front end using MapLibre.

## Data flow
1. ENC/CM93/GeoTIFF sources are converted to MBTiles or COG.
2. `registry.scan` walks the data directories and records metadata in `registry.sqlite`.
3. `/charts` exposes available datasets.
4. Tile routes serve vector and raster tiles consumed by the client.

## Setup
Stage `server-styling/dist` with built styles and sprites. Useful environment variables:
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
Pragmas: `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA busy_timeout=5000;`. Backup via `sqlite3 registry.sqlite ".backup registry.bak"`.

## Tile APIs
- `GET /charts` → `{ base: [..], enc: { datasets: [...] } }`
- `GET /tiles/enc/{ds}/{z}/{x}/{y}?fmt=mvt`
- `GET /tiles/geotiff/{id}/{z}/{x}/{y}.png`
- `GET /titiler/*`
- `GET /metrics`, `GET /healthz`

## Frontend hooks
`createMapAPI` exposes:
- `setBase(kind, id?)`
- `setDataset(id, bounds?)`
- `setTheme(theme)`
- `setMarinerParams(p)`

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
Unit tests and style coverage run on CI; registry and style assets must be present and coverage remains at 100%.

## Troubleshooting
- Missing `ETag` or `Cache-Control` headers: ensure tileserver middleware is active.
- CORS errors: confirm `allow_origins=["*"]`.
- Empty tiles: check dataset IDs and registry scan.
- Missing assets: rebuild `server-styling/dist` and rerun import tools.
