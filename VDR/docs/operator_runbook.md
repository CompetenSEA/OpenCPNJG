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

## Import ENC / CM93

```bash
# ENC → MBTiles (MVT)
python VDR/chart-tiler/tools/import_enc.py \
  --src /charts/ENC/US5NY1CM.000 \
  --id us5ny1cm --maxzoom 15

# place pre-built MBTiles manually
mv *.mbtiles VDR/chart-tiler/data/enc/

# CM93 (requires adapter)
export OPENCN_CM93_CLI=/opt/opencpn/bin/cm93_to_s57
python VDR/chart-tiler/tools/import_cm93.py --src /charts/CM93/region/

# GeoTIFF → COG + register
python VDR/chart-tiler/tools/import_geotiff.py --src /charts/raster/harbor.tif

# refresh registry if needed
curl -X POST localhost:8000/charts/scan
```

### Import ENC locally

When real cells are unavailable (e.g. in CI) synthesise a tiny fixture and
register it with the tiler:

```bash
python VDR/chart-tiler/tools/make_mbtiles_fixture.py \
  --out VDR/chart-tiler/data/enc/sample.mbtiles --scamin
curl -X POST localhost:8000/charts/scan
```

## Select Base Map

The web client reads `/charts` to populate the base picker.  Toggle between
`osm`, `geotiff` and `enc` bases at runtime without reloading the page.

GeoTIFF tiles are cached in-process.  Tune size via `GEO_LRU_SIZE` (default 256)
and enable WEBP encoding with `GEO_WEBP=1`.  Metrics for cache hits and render
errors are exposed on `/metrics`.

Vector MBTiles caching is controlled via `MBTILES_CACHE_SIZE` (default 1024).
Redis TTL for tile responses is set with `REDIS_TTL` (seconds).
