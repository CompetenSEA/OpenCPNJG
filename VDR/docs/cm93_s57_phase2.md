# CM93 / S-57 Import How-To

Phase 2 introduces real importers for vector ENC/CM93 data and raster
GeoTIFFs.  The tools live under `VDR/chart-tiler/tools/` and write artefacts
beneath `chart-tiler/data/`.

## CLI usage

```bash
# ENC → MBTiles (MVT) + register
python VDR/chart-tiler/tools/import_enc.py \
  --src /charts/ENC/US5NY1CM/ \
  --respect-scamin --maxzoom 15

# CM93 (requires adapter)
export OPENCN_CM93_CLI=/opt/opencpn/bin/cm93_to_s57
python VDR/chart-tiler/tools/import_cm93.py --src /charts/CM93/region/

# GeoTIFF → COG + register
python VDR/chart-tiler/tools/import_geotiff.py --src /charts/raster/harbor.tif
```

Each command is idempotent: rerunning skips work when input checksums match the
sidecar metadata.  Output files are placed in `data/mbtiles/` or
`data/geotiff/` and automatically registered with `/charts`.

## Optional admin API

When `IMPORT_API_ENABLED=1` the tile server exposes equivalent endpoints that
spawn the same scripts asynchronously:

* `POST /admin/import/enc` – JSON `{src, respectScamin?, name?}`
* `POST /admin/import/cm93` – JSON `{src}`
* `POST /admin/import/geotiff` – JSON `{src}`

Responses contain a task id and the server streams logs to stdout.

## Troubleshooting

* Missing `ogr2ogr` or `tippecanoe` – install GDAL and tippecanoe.  The
  importers print a `SKIP` message and exit successfully when tools are absent.
* Missing `OPENCN_CM93_CLI` – the CM93 importer quietly skips; set the
  environment variable to the conversion executable.
* Registry not updated – run `POST /charts/scan` or restart the server to pick
  up new artefacts.
