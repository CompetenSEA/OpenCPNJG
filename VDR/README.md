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
# GeoTIFF → COG + sidecar
python VDR/chart-tiler/tools/convert_geotiff.py input.tif --out-dir VDR/chart-tiler/data/geotiff

# Registry scan
python -m VDR.chart-tiler.registry --scan VDR/chart-tiler/data

# Run tileserver
uvicorn VDR.chart-tiler.tileserver:app --reload --port 8080

# Run web client (dev)
npm start --prefix VDR/web-client
```
Artefacts are written under `chart-tiler/data/*` and `server-styling/dist/*`.

## Testing
```
pytest VDR/chart-tiler/tests/test_convert_geotiff.py
pytest VDR/chart-tiler/tests/test_registry_scan.py
pytest VDR/chart-tiler/tests/test_tiles_geotiff.py
npm test --prefix VDR/web-client
# optional
pytest VDR/server-styling/tests
```

See `docs/map_pipeline.md` for full pipeline and database guidance.
