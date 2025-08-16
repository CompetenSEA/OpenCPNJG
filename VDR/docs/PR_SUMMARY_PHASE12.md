**Summary**

- Default to respecting SCAMIN when generating vector tiles, deriving `tippecanoe.minzoom` from the `SCAMIN` attribute. Users can opt out via `--no-respect-scamin`.

**Testing**

- `pytest -q VDR/chart-tiler/tests/test_scamin_mapping.py`
- `pytest -q VDR/chart-tiler/tests`
