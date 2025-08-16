# Web Client

React client using MapLibre and deck.gl.  It loads styles from the tileserver and exposes AppMap hooks.

## Usage
```
npm start --prefix VDR/web-client
```
The URL supports:
- `base=osm|geotiff|enc`
- `theme=day|dusk|night`
- `safety`, `shallow`, `deep` mariner params

## Tests
```
npm test --prefix VDR/web-client
```
