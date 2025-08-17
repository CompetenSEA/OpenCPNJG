# Web Client

React client using MapLibre and deck.gl.  It loads styles from the tileserver and exposes AppMap hooks. ENC datasets are the default base layer.

`fetchCharts()` in `src/features/charts` queries the `/charts` registry endpoint and
returns available datasets. Vector tiles are retrieved from
`/tiles/enc/{id}/{z}/{x}/{y}` and the map applies S‑52 sprite and color
definitions loaded from `assets/s52/` at startup.

## Usage
```
npm start --prefix VDR/web-client
```
The URL supports:
- `base=osm|geotiff|enc`
- `theme=day|dusk|night`
- `safety`, `shallow`, `deep` mariner params

`createMapAPI` exposes helpers:
- `setBase(kind, id?)` – switch base layer or ENC dataset while preserving mariner params.
- `setDataset(id, bounds?)` – set ENC dataset and optionally fit bounds.
- `setMarinerParams(p)` – update S‑52 safety contours.

## Tests
```
npm test --prefix VDR/web-client
```
