# Chart Tiler

FastAPI service that reads `registry.sqlite` and serves vector/raster tiles from MBTiles or COG sources.

## Endpoints
```
GET /charts
GET /charts/{id}
GET /config/contours
GET /config/datasource
GET /tiles/enc/{ds}/{z}/{x}/{y}?fmt=mvt
GET /tiles/geotiff/{id}/{z}/{x}/{y}.png
GET /titiler/*
GET /metrics
GET /healthz
```

## Cache keys
Tiles are cached by `fmt:ds:z/x/y:safety,shallow,deep`. Set `MBTILES_CACHE_SIZE` to tune the in‑memory LRU.

## Registry database
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

## Backup/restore
Use the `.backup` command above; restore by copying the backup over `registry.sqlite`.

## Tests
```
pytest VDR/chart-tiler/tests/test_convert_geotiff.py
pytest VDR/chart-tiler/tests/test_registry_scan.py
pytest VDR/chart-tiler/tests/test_tiles_geotiff.py
```

See `../docs/map_pipeline.md` for a broader pipeline overview.
