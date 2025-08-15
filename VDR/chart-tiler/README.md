# Chart Tiler

This module provides a Python based pipeline for converting nautical chart
datasets into web friendly tile sets. It focuses on S‑57 ENC data but exposes
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

## Metadata ingestion

`ingest_charts.py` reads CM93/S‑57 dictionaries via the `charts_py` bindings and
populates a `charts.sqlite` database with `object_class`, `attribute_class` and
`chart_metadata` tables:

```
python ingest_charts.py
```

### SQLite schema

The generated ``charts.sqlite`` contains three simple tables used by the tile
server at runtime:

``object_class``
: ``id`` (integer primary key), ``acronym`` (e.g. ``BOYSPP``) and human readable
  ``name``.

``attribute_class``
: ``id`` (integer primary key), ``acronym`` and ``name`` fields mirroring the
  S‑57 attribute dictionary.

``chart_metadata``
: ``key``/``value`` pairs for global information such as the chart edition.

Running the ingestion script multiple times is safe – rows are replaced on
conflict, keeping the database idempotent.

## FastAPI tile service

`tileserver.py` exposes `/tiles/{z}/{x}/{y}?fmt=png` (or `fmt=mvt`) using only
the day palette. It keeps an LRU memory cache and can optionally use Redis when
`REDIS_URL` is set. Prometheus metrics `tile_gen_ms` and `cache_hits` are
available at `/metrics`.

```
uvicorn tileserver:app --reload
```

## Headless render CLI

`render_tile.py z x y` generates a PNG tile for pixel‑diff regression tests:

```
python render_tile.py 0 0 0 --output tile.png
```

Use the resulting image as a baseline for comparison in CI, storing it outside
of the repository.
