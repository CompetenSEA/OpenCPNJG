from __future__ import annotations

import sys
from pathlib import Path

import mapbox_vector_tile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mvt_builder import encode_mvt


def _decode(tile: bytes):
    return mapbox_vector_tile.decode(tile)


def test_layers_and_precision():
    layers = {
        "features_points": [
            {"geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "properties": {"OBJL": "BOYSPP"}}
        ],
        "features_lines": [
            {
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[0.0, 0.0], [1.0, 1.0]],
                },
                "properties": {"OBJL": "COALNE"},
            }
        ],
        "soundings": [
            {"geometry": {"type": "Point", "coordinates": [0.5, 0.5]}, "properties": {"OBJL": "SOUNDG"}}
        ],
    }
    tile = encode_mvt(layers)
    assert len(tile) < 200 * 1024
    data = _decode(tile)
    assert set(data.keys()) == {"features_points", "features_lines", "soundings"}
    for layer in data.values():
        for feat in layer["features"]:
            geom = feat["geometry"]
            coords: list[tuple[int, int]]
            if geom["type"] == "Point":
                coords = [tuple(geom["coordinates"])]
            else:
                coords = [tuple(pt) for pt in geom["coordinates"]]
            for x, y in coords:
                assert isinstance(x, int) and isinstance(y, int)
                assert 0 <= x <= 4096 and 0 <= y <= 4096
