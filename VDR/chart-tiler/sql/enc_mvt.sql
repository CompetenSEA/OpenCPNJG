-- ENC Mapbox Vector Tile generation helpers
-- This function assembles the tile by building individual layers for points,
-- lines and soundings.  Geometries are simplified and quantised depending on
-- zoom level and encoded using ST_AsMVT with EXTENT=4096.

CREATE OR REPLACE FUNCTION enc_mvt(z integer, x integer, y integer)
RETURNS TABLE(layer text, tile bytea) AS $$
WITH bounds AS (
    SELECT ST_TileEnvelope(z, x, y) AS geom
),
params AS (
    SELECT
        CASE
            WHEN z < 10 THEN 50
            WHEN z < 12 THEN 10
            WHEN z < 14 THEN 2
            ELSE 0
        END AS simplify,
        CASE
            WHEN z < 10 THEN 1
            WHEN z < 14 THEN 0.1
            ELSE 0.01
        END AS quantize
),
raw AS (
    SELECT f.objl, f.geom
    FROM enc_features f, bounds
    WHERE ST_Intersects(f.geom, bounds.geom)
),
points AS (
    SELECT ST_AsMVTGeom(
               ST_QuantizeCoordinates(
                   ST_SimplifyPreserveTopology(f.geom, params.simplify),
                   params.quantize
               ),
               bounds.geom, 4096, 64, true
           ) AS geom,
           f.objl
    FROM raw f, bounds, params
    WHERE GeometryType(f.geom) = 'POINT' AND f.objl <> 'SOUNDG'
),
lines AS (
    SELECT ST_AsMVTGeom(
               ST_QuantizeCoordinates(
                   ST_SimplifyPreserveTopology(f.geom, params.simplify),
                   params.quantize
               ),
               bounds.geom, 4096, 64, true
           ) AS geom,
           f.objl
    FROM raw f, bounds, params
    WHERE GeometryType(f.geom) <> 'POINT'
),
snd AS (
    SELECT ST_AsMVTGeom(
               ST_QuantizeCoordinates(
                   ST_SimplifyPreserveTopology(f.geom, params.simplify),
                   params.quantize
               ),
               bounds.geom, 4096, 64, true
           ) AS geom,
           f.objl
    FROM raw f, bounds, params
    WHERE f.objl = 'SOUNDG'
)
SELECT 'features_points' AS layer,
       ST_AsMVT(points, 'features_points', 4096, 'geom') AS tile
FROM points
UNION ALL
SELECT 'features_lines' AS layer,
       ST_AsMVT(lines, 'features_lines', 4096, 'geom') AS tile
FROM lines
UNION ALL
SELECT 'soundings' AS layer,
       ST_AsMVT(snd, 'soundings', 4096, 'geom') AS tile
FROM snd;
$$ LANGUAGE SQL IMMUTABLE;
