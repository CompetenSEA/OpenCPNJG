-- CM93 initial database schema

-- Cells covering CM93 chart tiles
CREATE TABLE IF NOT EXISTS cm93_cells (
    cell_id text PRIMARY KEY,
    bounds geometry(Polygon, 4326)
);

-- Point features
CREATE TABLE IF NOT EXISTS cm93_pts (
    id bigserial PRIMARY KEY,
    cell_id text NOT NULL REFERENCES cm93_cells(cell_id),
    objl integer NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    attrs jsonb
);
CREATE INDEX idx_cm93_pts_geom ON cm93_pts USING GIST (geom);
CREATE INDEX idx_cm93_pts_objl ON cm93_pts (objl);
CREATE INDEX idx_cm93_pts_cell ON cm93_pts (cell_id);

-- Line features
CREATE TABLE IF NOT EXISTS cm93_ln (
    id bigserial PRIMARY KEY,
    cell_id text NOT NULL REFERENCES cm93_cells(cell_id),
    objl integer NOT NULL,
    geom geometry(MultiLineString, 4326) NOT NULL,
    attrs jsonb
);
CREATE INDEX idx_cm93_ln_geom ON cm93_ln USING GIST (geom);
CREATE INDEX idx_cm93_ln_objl ON cm93_ln (objl);
CREATE INDEX idx_cm93_ln_cell ON cm93_ln (cell_id);

-- Area features
CREATE TABLE IF NOT EXISTS cm93_ar (
    id bigserial PRIMARY KEY,
    cell_id text NOT NULL REFERENCES cm93_cells(cell_id),
    objl integer NOT NULL,
    geom geometry(MultiPolygon, 4326) NOT NULL,
    attrs jsonb
);
CREATE INDEX idx_cm93_ar_geom ON cm93_ar USING GIST (geom);
CREATE INDEX idx_cm93_ar_objl ON cm93_ar (objl);
CREATE INDEX idx_cm93_ar_cell ON cm93_ar (cell_id);

-- Label points
CREATE TABLE IF NOT EXISTS cm93_labels (
    id bigserial PRIMARY KEY,
    cell_id text NOT NULL REFERENCES cm93_cells(cell_id),
    objl integer NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    text text,
    attrs jsonb
);
CREATE INDEX idx_cm93_labels_geom ON cm93_labels USING GIST (geom);
CREATE INDEX idx_cm93_labels_objl ON cm93_labels (objl);
CREATE INDEX idx_cm93_labels_cell ON cm93_labels (cell_id);

-- Light features
CREATE TABLE IF NOT EXISTS cm93_lights (
    id bigserial PRIMARY KEY,
    cell_id text NOT NULL REFERENCES cm93_cells(cell_id),
    pt geometry(Point, 4326) NOT NULL,
    attrs jsonb
);
CREATE INDEX idx_cm93_lights_pt ON cm93_lights USING GIST (pt);
CREATE INDEX idx_cm93_lights_cell ON cm93_lights (cell_id);

-- Provenance metadata for imports
CREATE TABLE IF NOT EXISTS import_provenance (
    table_name text PRIMARY KEY,
    src_path text,
    src_sha256 text,
    imported_at timestamptz DEFAULT now()
);

-- SCAMIN rules
CREATE TABLE IF NOT EXISTS cm93_scamin (
    objl integer PRIMARY KEY,
    zmin integer NOT NULL,
    zmax integer NOT NULL
);

INSERT INTO cm93_scamin (objl, zmin, zmax) VALUES
    (71, 0, 16),   -- LNDARE
    (42, 0, 16),   -- DEPARE
    (43, 9, 16),   -- DEPCNT
    (30, 0, 16),   -- COALNE
    (129, 10, 16), -- SOUNDG
    (159, 12, 16), -- WRECKS
    (86, 12, 16);  -- OBSTRN

CREATE OR REPLACE FUNCTION apply_scamin(objl int, z int)
RETURNS boolean AS $$
    SELECT COALESCE(
        (SELECT $2 BETWEEN zmin AND zmax FROM cm93_scamin WHERE objl = $1),
        TRUE
    );
$$ LANGUAGE SQL IMMUTABLE;
