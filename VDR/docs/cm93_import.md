# CM93 Import

This module ingests CM93 datasets into the VDR database.

## CM93 detail parity

The original OpenCPN detail slider maps to zoom band filtering:

- Object classes are assigned to bands in `chart-tiler/config/portrayal/cm93_schemas.yml`.
- `cm93_rules.zoom_band_for(objl)` yields the band name; the server selects features accordingly.
- Minimum visibility scales are declared in `chart-tiler/config/portrayal/scamin.yml` and applied via `cm93_rules.apply_scamin`.

Together these rules approximate the CM93 “detail slider” and `SCAMIN` behaviour without replicating the C++ implementation.

## Native converter

The importer prefers a small optional C++ helper, `cm93_convert`, when
present on the `PATH`. The tool emits GeoJSON layers (`pts`, `ln`, `ar`)
matching our canonical schema【F:VDR/docs/opencpn_cm93_notes.md†L41-L46】.
If the binary is absent the importer falls back to the existing GDAL
workflow or pre-converted sources.

Example invocation:

```
cm93_convert --src ./cm93 --out ./out --schema vdr
```

## Benchmark methodology

Measure the time to convert a representative dataset with and without the
native converter. Record CPU, memory and output sizes; fill in results
once real data is available.
