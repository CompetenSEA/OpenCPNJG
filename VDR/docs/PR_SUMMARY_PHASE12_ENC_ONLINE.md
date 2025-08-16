# Phase 12 – ENC Online

* encode S‑57 to MBTiles with SCAMIN aware minzoom
* tileserver streams `/tiles/enc` from MBTiles with private metrics registry
* frontend defaults to ENC base and propagates mariner parameters
* docs describe local ENC ingestion and MBTiles format

## Commands

```
python VDR/chart-tiler/tools/make_mbtiles_fixture.py --out VDR/chart-tiler/data/enc/sample.mbtiles --scamin
uvicorn VDR.chart-tiler.tileserver:app --reload
curl -s localhost:8000/charts?kind=enc | jq .
```

## Perf Notes

LRU cache size tunable via `MBTILES_CACHE_SIZE`.

## Risks & Rollback

Fallback to previous CM93 endpoint is retained.  Remove `MBTILES_PATH` to disable
ENC serving.
