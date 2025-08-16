# CM93 / S-57 Phase‑2 Readiness

The current architecture defers ingesting CM93 and S‑57 data until a later
phase.  Hooks are nevertheless in place so the data can be enabled without
structural changes:

* `OPENCN_CM93_CLI` – optional environment variable that points to a CM93
  conversion tool.  When unset the system skips CM93 processing.
* SCAMIN → `minzoom` mapping is implemented in the tile server behind a flag so
  ENC data can downsample gracefully.
* Styling uses stable layer identifiers and the `metadata.maplibre:s52` token so
  additional symbol sets can be introduced without breaking existing layers.

### OBJL → MVT design

Future CM93/S‑57 import will map object classes (OBJL) into Mapbox Vector Tile
source layers named `features`.  Pre‑classification fields already supported in
Phase 1 include `Lights`, `Navaids`, `Hazards` and `Depths`.

### Test plan (for when data arrives)

1. Convert sample CM93/S‑57 datasets with the external CLI.
2. Import into the registry and verify `/charts` includes the new records.
3. Render tiles and confirm SCAMIN filtering behaves as expected.
