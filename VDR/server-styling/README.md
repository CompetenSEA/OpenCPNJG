# Server Styling

Builds MapLibre styles and sprites from OpenCPN S‑52 assets and reports coverage metrics.

## Assets staging
```
python VDR/server-styling/sync_opencpn_assets.py --lock VDR/server-styling/opencpn-assets.lock --dest VDR/server-styling/dist/assets/s52 --force
```

## Sprite & style build
```
python VDR/server-styling/tools/build_all_styles.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&safety={safety}&shallow={shallow}&deep={deep}" --sprite-base "/sprites/s52-day" --sprite-prefix "s52-" --glyphs "/glyphs/{fontstack}/{range}.pbf" --emit-name "OpenCPN S-52 {palette}" --auto-cover --labels
node VDR/server-styling/tools/validate_style.mjs VDR/server-styling/dist/style.s52.day.json
```
Generated styles live under `server-styling/dist/` with day/dusk/night palettes.

The tileserver serves these assets at `/style/s52.{palette}.json` and `/sprites/s52-day.{json|png}` with caching headers.

## Coverage tools
```
python VDR/server-styling/s52_coverage.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml
python VDR/server-styling/tools/update_docs_from_coverage.py --docs VDR/docs/s52s57cm93.md --coverage VDR/server-styling/dist/coverage/style_coverage.json --symbols VDR/server-styling/dist/coverage/symbols_seen.txt
```
Coverage reports gate CI; presence must remain 100% and catalogue deltas are tracked.

## Tests
```
pytest VDR/server-styling/tests
```
