# Chart Registry

`registry.py` maintains a small SQLite database listing available chart sources
(MBTiles, GeoTIFF and optional OSM base layers).  The registry is refreshed on
server start and cached in memory for five minutes.

FastAPI endpoints expose the data:

- `GET /charts` – list records with optional `kind`, `q`, `page` and
  `pageSize` filters.
- `GET /charts/{id}` – chart detail.
- `GET /charts/{id}/thumbnail` – optional thumbnail if present on disk.

Importers inspect `.mbtiles` and `.cog.json` files from the data directory.
Virtual OSM entries are added when `OSM_USE_COMMUNITY=true` (default).
