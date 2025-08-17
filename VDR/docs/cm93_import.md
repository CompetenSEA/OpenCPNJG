# CM93 Import

This module ingests CM93 datasets into the VDR database.

## CM93 detail parity

The original OpenCPN detail slider maps to zoom band filtering:

- Object classes are assigned to bands in `chart-tiler/config/portrayal/cm93_schemas.yml`.
- `cm93_rules.zoom_band_for(objl)` yields the band name; the server selects features accordingly.
- Minimum visibility scales are declared in `chart-tiler/config/portrayal/scamin.yml` and applied via `cm93_rules.apply_scamin`.

Together these rules approximate the CM93 “detail slider” and `SCAMIN` behaviour without replicating the C++ implementation.

## Native converter

The importer prefers a small optional C++ helper, `cm93_convert`. The
search order is:

1. The `OPENCN_CM93_CLI` environment variable.
2. `cm93_convert` on the `PATH`.
3. GDAL-based conversion.

The helper emits GeoJSON layers (`pts`, `ln`, `ar`) matching the canonical
schema【F:VDR/docs/opencpn_cm93_notes.md†L41-L46】 and additionally writes a
GeoPackage with `cm93_pts`, `cm93_ln` and `cm93_ar` tables. If the binary is
absent the importer logs the decision and falls back to the GDAL workflow or
pre-converted sources.

Example invocation:

```
cm93_convert --src ./cm93 --out ./out --schema vdr
```

Set the environment variable to override discovery:

```
export OPENCN_CM93_CLI=/opt/cm93_convert
```

## Benchmark methodology

Measure the time to convert a representative dataset with and without the
native converter. Record CPU, memory and output sizes; fill in results
once real data is available.
