# ENC MVT Schema

The ENC tiler emits Mapbox Vector Tiles with several layers, each targeting a
specific type of geometry or feature.  All geometries are clipped to the tile
bounds and encoded with an `EXTENT` of `4096`.

## Layers

| Layer name       | Geometry                | Zoom range | Notes |
|------------------|-------------------------|-----------|-------|
| `features_points`| point features except soundings | z0–22 | buoys, lights, beacons and other non-sounding points |
| `features_lines` | lines and polygons      | z0–22     | coastline, contours, area fills and other linear features |
| `soundings`      | point soundings (`OBJL` = `SOUNDG`) | z12–22 | depth soundings rendered separately |

## Generalisation

* Geometries are simplified using `ST_SimplifyPreserveTopology`.
* Coordinates are snapped using `ST_QuantizeCoordinates`.
* Tolerances vary by zoom level:

| Zoom | Simplify tolerance (metres) | Quantize tolerance (metres) |
|------|-----------------------------|-----------------------------|
| z < 10 | 50 | 1 |
| 10–11  | 10 | 0.1 |
| 12–13  | 2  | 0.1 |
| ≥ 14   | 0  | 0.01 |

These rules keep tiles small while retaining detail at higher zooms.  Soundings
(`SOUNDG`) appear from zoom 12 onwards to control density.
