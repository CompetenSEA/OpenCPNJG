Summary

Finalized S‑52 classification by promoting the nearest contour to safety when no exact match exists. Labels now scale with zoom (SOUNDG + seamarks). Built and served day/dusk/night styles. Added an opt‑in Raster MVP path that draws DEPARE/DEPCNT.

Testing

- `python VDR/server-styling/tools/stage_local_assets.py --repo-data data/s57data --dest VDR/server-styling/dist/assets/s52 --force`
- `python VDR/server-styling/tools/build_all_styles.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&safety={safety}&shallow={shallow}&deep={deep}" --source-name cm93 --source-layer features --sprite-base "/sprites/s52-day" --sprite-prefix "s52-" --glyphs "/glyphs/{fontstack}/{range}.pbf" --emit-name "OpenCPN S-52 {palette}" --auto-cover --labels`
- `pytest -q VDR/chart-tiler/tests/test_finalize_safety.py`
- `pytest -q VDR/chart-tiler/tests/test_tileserver.py`
- `pytest -q VDR/server-styling/tests/test_label_scaling.py`
- `pytest -q VDR/chart-tiler/tests/test_raster_mvp.py || true`
- `npm --prefix web-client ci || true`
- `npm --prefix web-client test || true`

Risks & Rollback

Finalize logic is deterministic and tile‑local; disable by setting a guard flag if needed. Raster MVP is opt‑in (fmt=png-mvp or env), defaulting to previous 1×1 behavior. Frontend falls back to day style and preset mariner params if endpoints are unavailable.
