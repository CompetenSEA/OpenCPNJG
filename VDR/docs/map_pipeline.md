# Map Pipeline

## Overview
The pipeline ingests ENC, CM93, and GeoTIFF charts, normalises them into a small SQLite registry, renders vector or raster tiles, and serves them to a MapLibre web client.  Styling assets are staged from OpenCPN S‑52 sources and compiled into MapLibre styles and sprites.

## Components
- **server-styling** – stages S‑52 assets, builds day/dusk/night MapLibre styles and sprites, and reports coverage metrics.
- **chart-tiler** – converts charts to COG or MBTiles, maintains the registry, and exposes FastAPI tile and registry endpoints.
- **web-client** – React/MapLibre client with deck.gl overlays and AppMap base/theme/mariner toggles.

## Data flow
`import` tools write artefacts under `chart-tiler/data/*` → `registry` scan records charts in `registry.sqlite` → `tileserver` reads MBTiles/COG and serves `/tiles/*` → `web-client` selects base and applies mariner params.

## Setup
- **Assets staging**: `python VDR/server-styling/sync_opencpn_assets.py --lock VDR/server-styling/opencpn-assets.lock --dest VDR/server-styling/dist/assets/s52 --force`
- **Style build**: `python VDR/server-styling/generate_sprite_json.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --output VDR/server-styling/dist/sprites/s52-day.json`
- **Coverage report**: `python VDR/server-styling/s52_coverage.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml`
- **Env vars**: `MBTILES_PATH`, `MBTILES_CACHE_SIZE`, `OSM_USE_COMMUNITY`, `IMPORT_API_ENABLED`.

## Build/Run
- GeoTIFF → COG + sidecar
  ```
  python VDR/chart-tiler/tools/convert_geotiff.py input.tif --out-dir VDR/chart-tiler/data/geotiff
  ```
- Registry scan (on server boot or CLI helper)
  ```
  python -m VDR.chart-tiler.registry --scan VDR/chart-tiler/data
  ```
- ENC / CM93 import
  ```
  python VDR/chart-tiler/tools/import_enc.py --src /charts/ENC/DS --respect-scamin --maxzoom 15
  python VDR/chart-tiler/tools/import_cm93.py --src /charts/CM93/region/
  ```
- Build all styles and sprites
  ```
  python VDR/server-styling/tools/build_all_styles.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&safety={safety}&shallow={shallow}&deep={deep}" --sprite-base "/sprites/s52-day" --sprite-prefix "s52-" --glyphs "/glyphs/{fontstack}/{range}.pbf" --emit-name "OpenCPN S-52 {palette}" --auto-cover --labels
  ```
- Validate one style
  ```
  node VDR/server-styling/tools/validate_style.mjs VDR/server-styling/dist/style.s52.day.json
  ```
- Run tileserver
  ```
  uvicorn VDR.chart-tiler.tileserver:app --reload --port 8080
  ```
- Web client tests
  ```
  npm test --prefix VDR/web-client
  ```

## Registry/DB
Schema (SQLite)
```sql
-- charts registry
CREATE TABLE IF NOT EXISTS charts (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,           -- enc|geotiff|osm
  name TEXT NOT NULL,
  path TEXT,                    -- local path for enc/geotiff
  url  TEXT,                    -- remote URL (when applicable)
  bbox TEXT,                    -- JSON array [w,s,e,n]
  minzoom INTEGER,
  maxzoom INTEGER,
  updated_at TEXT,
  tags TEXT,                    -- JSON array
  status TEXT                   -- ready|disabled|error
);
CREATE TABLE IF NOT EXISTS artifacts (
  chart_id TEXT,
  type TEXT,                    -- sidecar|thumbnail|cog|mbtiles
  path TEXT,
  sha256 TEXT,
  created_at TEXT,
  PRIMARY KEY(chart_id, type, path)
);
CREATE INDEX IF NOT EXISTS idx_charts_kind ON charts(kind);
CREATE INDEX IF NOT EXISTS idx_charts_name ON charts(name);
CREATE INDEX IF NOT EXISTS idx_artifacts_chart ON artifacts(chart_id);
```
Migrations bump `PRAGMA user_version`; keep idempotent SQL in `chart-tiler/migrations/`.  Use `journal_mode=WAL`, `synchronous=NORMAL`, and `busy_timeout=5000`.  Back up with `sqlite3 registry.sqlite ".backup registry.bak"` before large scans.

## Tile APIs
```
GET /charts?kind={enc|geotiff|osm}&q=&page=&pageSize=
GET /charts/{id}
GET /tiles/geotiff/{id}/{z}/{x}/{y}.png (MapProxy→TiTiler)
GET /titiler/* (mounted sub-app)
GET /metrics, GET /healthz
```

## Frontend hooks
AppMap exposes `base` (`osm|geotiff|enc`), `theme` (`day|dusk|night`), and mariner params (`safety`, `shallow`, `deep`) as URL/search parameters and toggles.  Theme and mariner settings propagate to tile requests.

## Testing
```
pytest VDR/chart-tiler/tests/test_convert_geotiff.py
pytest VDR/chart-tiler/tests/test_registry_scan.py
pytest VDR/chart-tiler/tests/test_tiles_geotiff.py
npm test --prefix VDR/web-client
# optional
pytest VDR/server-styling/tests
```

## CI/CD
CI stages S‑52 assets, builds all palettes, validates MapLibre styles, enforces coverage and registry gates, and runs the full test matrix.  Artefacts (`style.s52.*.json`, sprites, COG/MBTiles samples) are produced under `server-styling/dist` and `chart-tiler/data`.

## Troubleshooting
- Missing GDAL/Tippecanoe: import tools skip gracefully but tile endpoints may 404.
- Registry locked: ensure no other process holds `registry.sqlite` and use WAL mode.
- Tiles returning 500: check `GET /metrics` and `GET /healthz` for diagnostics.
- Web client blank: verify base URL and that styles and sprites were built.

