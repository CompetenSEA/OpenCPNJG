# Operator Runbook

## Refresh the Registry

```bash
cd VDR/chart-tiler
python -c "from registry import get_registry; get_registry().scan([Path('data')])"  # refresh
# or via API
curl -X POST localhost:8000/charts/scan
```

## Import a GeoTIFF

```bash
cd VDR/chart-tiler
make geotiff-cog SRC=/charts/foo.tif
```

## Select Base Map

The web client reads `/charts` to populate the base picker.  Toggle between
`osm`, `geotiff` and `enc` bases at runtime without reloading the page.

GeoTIFF tiles are cached in-process.  Tune size via `GEO_LRU_SIZE` (default 256)
and enable WEBP encoding with `GEO_WEBP=1`.  Metrics for cache hits and render
errors are exposed on `/metrics`.
