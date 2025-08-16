#!/usr/bin/env python3
"""Create a tiny ENC MBTiles fixture for tests.

The fixture contains a single tile (z0/x0/y0) with a couple of synthetic
features so that the vector tile is non-empty.  The goal is to provide a
network-free sample for unit tests and local development when real ENC data is
unavailable.  The resulting file is intentionally tiny and is not meant for
navigation.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import List, Dict

from mvt_builder import encode_mvt  # type: ignore


def _build_features(include_scamin: bool) -> List[Dict]:
    feats: List[Dict] = []
    props: Dict[str, object]

    # Simple land area polygon
    props = {"OBJL": "LNDARE"}
    if include_scamin:
        props["SCAMIN"] = 45000
    feats.append(
        {
            "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
            "properties": props,
        }
    )

    # Depth area
    props = {"OBJL": "DEPARE", "DRVAL1": 0, "DRVAL2": 5}
    if include_scamin:
        props["SCAMIN"] = 45000
    feats.append({"geometry": {"type": "Polygon", "coordinates": [[[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8], [0.2, 0.2]]]}, "properties": props})

    # Contour line
    props = {"OBJL": "DEPCNT", "VALDCO": 10}
    if include_scamin:
        props["SCAMIN"] = 45000
    feats.append({"geometry": {"type": "LineString", "coordinates": [[0, 0.5], [1, 0.5]]}, "properties": props})

    # Sounding
    props = {"OBJL": "SOUNDG", "VALSOU": 3}
    if include_scamin:
        props["SCAMIN"] = 45000
    feats.append({"geometry": {"type": "Point", "coordinates": [0.5, 0.5]}, "properties": props})

    return feats


def make_fixture(path: Path, include_scamin: bool) -> None:
    feats = _build_features(include_scamin)
    tile = encode_mvt(feats)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE metadata (name TEXT, value TEXT)")
    cur.execute("CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)")
    cur.executemany(
        "INSERT INTO metadata VALUES (?,?)",
        [
            ("name", "enc_fixture"),
            ("format", "pbf"),
            ("bounds", "0,0,1,1"),
            ("minzoom", "0"),
            ("maxzoom", "14"),
        ],
    )
    cur.execute("INSERT INTO tiles VALUES (0,0,0,?)", (sqlite3.Binary(tile),))
    conn.commit()
    conn.close()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, help="Output .mbtiles path")
    p.add_argument("--scamin", action="store_true", help="Include SCAMIN attributes")
    args = p.parse_args()
    make_fixture(Path(args.out), args.scamin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
