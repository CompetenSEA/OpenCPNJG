# Server Styling

Builds MapLibre styles and sprites from OpenCPN S‑52 assets and reports coverage metrics.

## Regenerating assets
```
python VDR/server-styling/sync_opencpn_assets.py --force
```
Assets are downloaded according to `opencpn-assets.lock` and written to `server-styling/assets/`.

## S-52 sprite assets
```
python VDR/server-styling/build_s52_assets.py
# or
make -C VDR/server-styling assets
```
Sprite sheets, colour tables and metadata are written to `VDR/assets/s52/`.

## Sprite & style build
```
python VDR/server-styling/build_style_json.py --palette day
```
This bundles the assets under `server-styling/dist/`, generates the sprite atlas and writes `style.s52.{palette}.json`. The style references `/tiles/cm93-core.json` and `/tiles/cm93-label.json` sources and expects glyphs at `/glyphs/{fontstack}/{range}.pbf` and sprites at `/sprites/s52-{palette}`.

Generated output lives under `server-styling/dist/`.

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
