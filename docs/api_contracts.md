# API Contracts

## `query_tile_mvt`

`query_tile_mvt` emits a gzip-compressed Mapbox Vector Tile. The encoder
uses vtzero and zlib with a fixed header so the output is deterministic.
For empty tiles the payload remains under 2 KB and the gzip CRC32 hash is
stable.
The OpenCPN API exposes a minimal REST surface for chart queries. This document locks down the final request and response semantics.

## Endpoint Headers
- `X-OCPN-Trace` – correlation identifier echoed in logs.
- `X-OCPN-Bounds` – optional bounding box following the schema below.
- `Content-Type` – all responses use `application/json`.

## Bounds Schema
```json
{
  "north": float,
  "south": float,
  "east": float,
  "west": float
}
```
Values are expressed in decimal degrees and must satisfy `south <= north` and `west <= east` with wrap-around handled by clients.

## On-Wire Attribute Conventions
- JSON keys use `snake_case`.
- All timestamps are UTC ISO 8601 strings.
- Enumerations serialize as lowercase strings.

## Performance Budget
Each endpoint must respond within **200 ms** at the 95th percentile and return payloads under **64 KB**.

## Test Expectations
Contract tests in `test/api` validate headers, bounds parsing, and attribute naming. Run `ctest` after schema changes to ensure backward compatibility.