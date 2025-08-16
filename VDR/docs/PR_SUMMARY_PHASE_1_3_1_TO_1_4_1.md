# Phase 1.3/1.4 Addenda Summary

This patch series introduces the GeoTIFF conversion tool, a cached chart
registry with new FastAPI endpoints, a placeholder GeoTIFF tile service and a
MapLibre AppMap capable of switching between OSM, GeoTIFF and ENC bases.  It also
documents CM93/S‑57 readiness and provides operator notes for importing charts
and refreshing the registry.

## Testing

- `pytest VDR/chart-tiler/tests/test_convert_geotiff.py`
- `pytest VDR/chart-tiler/tests/test_registry_scan.py`
- `pytest VDR/chart-tiler/tests/test_tiles_geotiff.py`
- `pytest VDR/chart-tiler/tests/test_charts_api.py`
- `npm test --prefix VDR/web-client`
