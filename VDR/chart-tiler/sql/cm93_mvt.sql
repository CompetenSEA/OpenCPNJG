-- CM93 Mapbox Vector Tile helpers
-- These functions are placeholders demonstrating the intended PostGIS queries.

CREATE OR REPLACE FUNCTION cm93_mvt_core(z integer, x integer, y integer)
RETURNS bytea AS $$
    WITH bounds AS (
        SELECT ST_TileEnvelope(z, x, y) AS geom
    ),
    mvtgeom AS (
        SELECT ST_AsMVTGeom(ST_Intersection(f.geom, bounds.geom), bounds.geom, 4096, 64, true) AS geom,
               f.objl
        FROM cm93_features f, bounds
        WHERE apply_scamin(f.objl, z)
    )
    SELECT ST_AsMVT(mvtgeom, 'features', 4096, 'geom') FROM mvtgeom;
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION cm93_mvt_label(z integer, x integer, y integer)
RETURNS bytea AS $$
    -- Text-only layer
    WITH bounds AS (
        SELECT ST_TileEnvelope(z, x, y) AS geom
    ),
    mvtgeom AS (
        SELECT ST_AsMVTGeom(ST_Intersection(f.geom, bounds.geom), bounds.geom, 4096, 64, true) AS geom,
               f.objl, f.text
        FROM cm93_labels f, bounds
        WHERE apply_scamin(f.objl, z)
    )
    SELECT ST_AsMVT(mvtgeom, 'features', 4096, 'geom') FROM mvtgeom;
$$ LANGUAGE SQL IMMUTABLE;
