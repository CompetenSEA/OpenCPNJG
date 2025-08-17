# Style API

## `/style/s52.{palette}.json`
Retrieves a MapLibre style sheet built from S-52 symbols. Replace `{palette}` with `day`, `dusk` or `night` to swap colour palettes. Responses include CORS headers (`Access-Control-Allow-Origin: *`) and are cached with `ETag` and `Cache-Control: public, max-age=3600`.

## `/charts`
Returns available chart datasets:
```json
{ "base": ["osm", "geotiff", "enc"], "enc": { "datasets": [ ... ] } }
```
The summary endpoint allows cross-origin requests and is served with `Cache-Control: no-store`.

## Palette toggling
Clients switch palettes by requesting the corresponding style URL (`/style/s52.day.json`, `/style/s52.dusk.json`, `/style/s52.night.json`). Each style file is CORS enabled and cached for one hour, so palette changes reuse the browser cache when available.
