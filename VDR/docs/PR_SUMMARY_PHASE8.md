### Summary

- Extend auto-cover to synthesize stub layers for S-57 object classes lacking S-52 lookups and record `OBJL-*` metadata tokens.
- Generate `s57_catalogue.json` and doc table summarizing catalogue coverage and missing classes.
- CI builds styles with catalogue backfill, enforces coverage thresholds, and refreshes docs.

### Testing

- `python VDR/server-styling/tools/stage_local_assets.py --repo-data data/s57data --dest VDR/server-styling/dist/assets/s52 --force`
- `python VDR/server-styling/tools/build_all_styles.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&safety={safety}&shallow={shallow}&deep={deep}" --source-name cm93 --source-layer features --sprite-base "/sprites/s52-day" --sprite-prefix "s52-" --glyphs "/glyphs/{fontstack}/{range}.pbf" --emit-name "OpenCPN S-52 {palette}" --auto-cover --s57-catalogue VDR/server-styling/dist/assets/s52/s57objectclasses.csv`
- `python VDR/server-styling/build_style_json.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url dummy --source-name src --source-layer lyr --sprite-base "/sprites/s52-day" --glyphs "/glyphs/{fontstack}/{range}.pbf" --palette day --auto-cover --labels --output VDR/server-styling/dist/style.s52.day.labels.json`
- `python VDR/server-styling/s52_coverage.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml`
- `python VDR/server-styling/tools/update_docs_from_coverage.py --docs VDR/docs/s52s57cm93.md --coverage VDR/server-styling/dist/coverage/style_coverage.json --portrayal VDR/server-styling/dist/coverage/portrayal_coverage.json --s57 VDR/server-styling/dist/coverage/s57_catalogue.json --symbols VDR/server-styling/dist/coverage/symbols_seen.txt`
- `pytest -q VDR/server-styling/tests/test_full_s52_coverage.py`
- `pytest -q VDR/server-styling/tests/test_s57_parity.py`
- `pytest -q VDR/server-styling/tests`
- `pytest -q VDR/chart-tiler/tests`

### Risks & Rollback

- Tooling heavy changes; roll back by reverting server-styling and doc updates to Phase 7.

