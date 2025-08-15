# Chart Tiler

This module provides a Python based pipeline for converting nautical chart
datasets into web friendly tile sets.  It focuses on S‑57 ENC data but exposes
hooks to plug in a CM93→S‑57 converter in the future.

## Features

* Generate **vector tiles** (MBTiles) using `tippecanoe`.
* Generate **raster tiles** as Cloud Optimised GeoTIFFs using GDAL.
* Optional SFTP upload helper for deploying to a Hostinger VPS.

```
python convert_charts.py US5MD11M.000 output/
```

The command above produces `US5MD11M.mbtiles` and `US5MD11M.tif` in the
`output` directory.
