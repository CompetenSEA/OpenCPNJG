# Vector Data Renderer (VDR)

End‑to‑end pipeline for nautical charts.  ENC, CM93 and GeoTIFF sources are converted to Cloud Optimised GeoTIFFs or MBTiles, registered in SQLite and served via FastAPI to a MapLibre web client.  Styling assets are derived from OpenCPN S‑52 resources.

## Core libraries
- Python 3.11+
- FastAPI + Uvicorn
- GDAL, Tippecanoe, TiTiler, MapProxy
- SQLite
- React + MapLibre GL + deck.gl

## Quickstart
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
Artefacts are written under `chart-tiler/data/*` and `server-styling/dist/*`.

See `docs/map_pipeline.md` for the full pipeline, database schema and testing matrix.

## Fonts and glyphs
Font binaries are intentionally excluded from version control. Fetch the fonts
listed in `server-styling/fonts.lock` into `assets/fonts/` and run
`node scripts/bake_glyphs.js` to produce `glyphs/{fontstack}/{range}.pbf`.
Copy the glyphs to your deployment target as needed.
