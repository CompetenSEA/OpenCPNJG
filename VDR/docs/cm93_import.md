# CM93 Import

This module ingests CM93 datasets into the VDR database.

## CM93 detail parity

The original OpenCPN detail slider maps to zoom band filtering:

- Object classes are assigned to bands in `chart-tiler/config/portrayal/cm93_schemas.yml`.
- `cm93_rules.zoom_band_for(objl)` yields the band name; the server selects features accordingly.
- Minimum visibility scales are declared in `chart-tiler/config/portrayal/scamin.yml` and applied via `cm93_rules.apply_scamin`.

Together these rules approximate the CM93 “detail slider” and `SCAMIN` behaviour without replicating the C++ implementation.
