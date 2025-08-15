# Phase 4 Summary

## What changed
- Documented CM93/S-57 to Web pipeline with auto-generated coverage section.
- Added hazard sprite offsets and prefix-safe consumption.
- CI now validates styles with Node validator and checks docs freshness.

## How to run
See commands in repository README or run:
```
python VDR/server-styling/sync_opencpn_assets.py --lock VDR/server-styling/opencpn-assets.lock --dest VDR/server-styling/dist/assets/s52 --force
python VDR/server-styling/generate_sprite_json.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --output VDR/server-styling/dist/sprites/s52-day.json
python VDR/server-styling/build_style_json.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&sc={sc}" --source-name cm93 --source-layer features --sprite-base "/sprites/s52-day" --sprite-prefix "s52-" --glyphs "/glyphs/{fontstack}/{range}.pbf" --safety-contour 10 --output VDR/server-styling/dist/style.s52.day.json
npm install --no-save @maplibre/maplibre-gl-style-spec
node VDR/server-styling/tools/validate_style.mjs VDR/server-styling/dist/style.s52.day.json
python VDR/server-styling/s52_coverage.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml
python VDR/server-styling/tools/update_docs_from_coverage.py --docs VDR/docs/s52s57cm93.md --coverage VDR/server-styling/dist/coverage/style_coverage.json --symbols VDR/server-styling/dist/coverage/symbols_seen.txt
pytest VDR/server-styling/tests -q
pytest VDR/chart-tiler/tests -q
```

## Risks & roll-back
- Offsets rely on symbol metadata; if anchors missing, icons render centered.
- Docs check only warns; stale coverage blocks can be refreshed via update_docs_from_coverage.py.

