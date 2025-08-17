-- CM93 Mapbox Vector Tile helpers
--
-- These PostGIS functions generate Mapbox Vector Tiles for CM93 data.  The
-- geometry tables are clipped to the requested tile and light sector geometry
-- is constructed on the fly.  Output properties use compact integer ``objl``
-- codes matching the dictionary exposed by ``/tiles/cm93/dict.json``.

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
    ),
    lightgeom AS (
        SELECT ST_AsMVTGeom(
                   ST_SimplifyPreserveTopology(
                       ST_Intersection(s.geom, bounds.geom),
                       CASE WHEN z < 14 THEN 50 ELSE 10 END,
                       true
                   ),
                   bounds.geom, 4096, 64, true) AS geom,
               8 AS objl
        FROM cm93_lights l
        JOIN LATERAL build_light_sectors(l.pt, l.attrs) AS s(geom) ON true,
             bounds
        WHERE z >= 12
    ),
    allgeom AS (
        SELECT * FROM mvtgeom
        UNION ALL
        SELECT * FROM lightgeom
    )
    SELECT ST_AsMVT(allgeom, 'features', 4096, 'geom') FROM allgeom;
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
    ),
    lightlabels AS (
        SELECT ST_AsMVTGeom(ST_Intersection(l.pt, bounds.geom), bounds.geom, 4096, 64, true) AS geom,
               8 AS objl,
               build_light_character(l.attrs) AS text
        FROM cm93_lights l, bounds
        WHERE z >= 12
    ),
    allgeom AS (
        SELECT * FROM mvtgeom
        UNION ALL
        SELECT * FROM lightlabels
    )
    SELECT ST_AsMVT(allgeom, 'features', 4096, 'geom') FROM allgeom;
$$ LANGUAGE SQL IMMUTABLE;
