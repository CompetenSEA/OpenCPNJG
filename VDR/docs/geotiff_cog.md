# GeoTIFF → Cloud Optimized GeoTIFF

Use `tools/convert_geotiff.py` to normalise incoming GeoTIFF charts into a
Cloud Optimized GeoTIFF (COG).  The script wraps `gdal_translate` with the
recommended options and writes a sidecar JSON file with spatial metadata.

```bash
cd VDR/chart-tiler
make geotiff-cog SRC=/path/to/input.tif
```

Output files are placed under `chart-tiler/data/geotiff` (ignored by git) and
are safe to regenerate – runs are skipped when the checksum matches the existing
sidecar.
