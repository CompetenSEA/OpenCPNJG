# API Contracts

## `query_tile_mvt`

`query_tile_mvt` emits a gzip-compressed Mapbox Vector Tile. The encoder
uses vtzero and zlib with a fixed header so the output is deterministic.
For empty tiles the payload remains under 2 KB and the gzip CRC32 hash is
stable.
