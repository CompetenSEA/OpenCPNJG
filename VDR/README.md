# Vector Data Renderer (VDR)

## Milestones

| Step | Tasks | Deliverables |
| --- | --- | --- |
| 0.1 Repository setup | \*Clone existing OpenCPN code into `/opencpn-libs`.<br>\*Create `/chart-tiler` (Python/FastAPI) and `/web-client` (React + MapLibre + deck.gl). | Mono‑repo with three folders and basic Dockerfile/compose. |
| 0.2 C++ core library | \*Use CMake to compile `src/cm93`, `src/s57chart`, `ps52plib` into shared **libcharts.so**.<br>\*Expose minimal C++ APIs: `load_cell`, `render_tile_png`, `render_tile_mvt`. | Versioned **libcharts.so** with documented headers. |
| 0.3 Python bindings | \*pybind11 wrapper exposing `generate_tile(bbox, z, fmt='png', palette='day')`.<br>\*Unit test: load sample CM93/S‑57 cell → generate one tile. | `charts_py` Python wheel; tests passing. |
| 0.4 Test data & CI | \*Place small CM93+S‑57 cells under `/testdata`.<br>\*GitHub Actions: build lib, build Python wheel, run smoke render (pixel diff). | Green CI; repeatable fixtures. |
| 0.5 Binary dependencies | \*Document binary assets and their origin.<br>\*Fetch or build binaries during CI rather than committing them. | Transparent binary provenance; clean repository history. |

## Binary Sources

The project relies on several binary artifacts which must **not** be committed. Build or copy them locally from trusted sources:

| Binary | Where needed | Source |
| --- | --- | --- |
| `libcharts.so` | `opencpn-libs` build output | Compiled via CMake from `src/cm93`, `src/s57chart`, and `ps52plib` in this repo. |
| `charts_py` wheel | `chart-tiler` Python package | Built with pybind11 bindings against `libcharts.so`. |
| Sample CM93 & S‑57 cells | `testdata/` | Obtain from official hydrographic offices (e.g., NOAA). Copy into place locally: `cp data/s57data/rastersymbols-day.png VDR/testdata/`. |
| GIS helpers (`tippecanoe`, `GDAL`) | `chart-tiler` tooling | Install from upstream releases or package managers during CI. |

Each of these binaries should be obtained during development or CI using download or build steps, keeping the Git history free of binary blobs.
