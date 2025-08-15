# Summary
- add `stage_local_assets.py` to copy S-52/S-57 assets from `data/s57data`
- support `--emit-name` in `build_all_styles.py`
- broaden style coverage checks and doc updater
- document staging flow and update coverage block
- add ingest test for all S-57 object classes

# Testing
- `python VDR/server-styling/tools/stage_local_assets.py --repo-data data/s57data --dest VDR/server-styling/dist/assets/s52 --force`
- `python VDR/server-styling/tools/build_all_styles.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&safety={safety}&shallow={shallow}&deep={deep}" --source-name cm93 --source-layer features --sprite-base "/sprites/s52-day" --sprite-prefix "s52-" --glyphs "/glyphs/{fontstack}/{range}.pbf"`
- `node VDR/server-styling/tools/validate_style.mjs VDR/server-styling/dist/style.s52.day.json`
- `python VDR/server-styling/s52_coverage.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml`
- `python VDR/server-styling/tools/update_docs_from_coverage.py --docs VDR/docs/s52s57cm93.md --coverage VDR/server-styling/dist/coverage/style_coverage.json --symbols VDR/server-styling/dist/coverage/symbols_seen.txt`
- `pytest -q VDR/chart-tiler/tests/test_s57_catalogue_ingest.py`
