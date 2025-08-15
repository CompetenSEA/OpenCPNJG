from __future__ import annotations

"""Deterministic synthetic datasource used for tests.

The datasource generates a small set of GeoJSON‑like features within the
provided bounding box.  The output is fully deterministic for a given tile
(z/x/y) so that unit tests remain stable.
"""

from typing import Iterable, Dict, Any, Tuple, List

BBox = Tuple[float, float, float, float]


def _rect_polygon(x1: float, y1: float, x2: float, y2: float) -> List[List[List[float]]]:
    """Return coordinates for a simple rectangle polygon."""

    return [[[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]]]


def features_for_tile(bbox: BBox, z: int, x: int, y: int) -> Iterable[Dict[str, Any]]:
    """Yield deterministic features for the given tile.

    The geometries are deliberately simple and only serve to exercise the
    server pipeline.
    """

    minx, miny, maxx, maxy = bbox
    midx = (minx + maxx) / 2.0
    midy = (miny + maxy) / 2.0

    # Land area covering left half of the tile -----------------------------
    yield {
        "geometry": {"type": "Polygon", "coordinates": _rect_polygon(minx, miny, midx, maxy)},
        "properties": {"OBJL": "LNDARE"},
    }

    # Two depth areas on the water side -----------------------------------
    # Shallow area
    yield {
        "geometry": {"type": "Polygon", "coordinates": _rect_polygon(midx, miny, maxx, midy)},
        "properties": {"OBJL": "DEPARE", "DRVAL1": 0.0, "DRVAL2": 5.0},
    }
    # Deeper area which flips classification around common safety contours
    yield {
        "geometry": {"type": "Polygon", "coordinates": _rect_polygon(midx, midy, maxx, maxy)},
        "properties": {"OBJL": "DEPARE", "DRVAL1": 10.0, "DRVAL2": 100.0},
    }

    # Depth contours with varying accuracy --------------------------------
    vals = [5.0, 10.0, 15.0]
    for i, v in enumerate(vals):
        x_coord = midx + (i + 1) * (maxx - midx) / 4.0
        yield {
            "geometry": {"type": "LineString", "coordinates": [[x_coord, miny], [x_coord, maxy]]},
            "properties": {
                "OBJL": "DEPCNT",
                "VALDCO": v,
                "QUAPOS": 3 if i == 1 else 1,  # Second contour marked low accuracy
            },
        }

    # Coastline separating land and water ---------------------------------
    yield {
        "geometry": {"type": "LineString", "coordinates": [[midx, miny], [midx, maxy]]},
        "properties": {"OBJL": "COALNE"},
    }

    # Soundings with different depths -------------------------------------
    sound_vals = [2.0, 15.0]
    for i, val in enumerate(sound_vals):
        sx = midx + (i + 1) * (maxx - midx) / 3.0
        sy = miny + (i + 1) * (maxy - miny) / 3.0
        yield {
            "geometry": {"type": "Point", "coordinates": [sx, sy]},
            "properties": {"OBJL": "SOUNDG", "VALSOU": val},
        }
