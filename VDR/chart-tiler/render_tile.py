"""CLI utility for rendering a single chart tile to PNG.

The script is intentionally tiny – it simply invokes
``charts_py.generate_tile`` for a given Web‑Mercator tile coordinate and writes
the resulting PNG to disk.  It is primarily used in automated tests where the
output is compared against a baseline image.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import charts_py


def tile_bounds(x: int, y: int, z: int) -> list[float]:
    """Return the bounding box for a Web‑Mercator tile."""

    n = 2 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return [lon_left, lat_bottom, lon_right, lat_top]


def main(z: int, x: int, y: int, output: Path) -> None:
    """Render tile ``(z, x, y)`` and write the PNG to *output*."""

    bbox = tile_bounds(x, y, z)
    opts = {"format": "png", "palette": "day", "safetyContour": 0.0}
    data = charts_py.generate_tile(bbox, z, opts)
    output.write_bytes(data)


if __name__ == "__main__":  # pragma: no cover - exercised via tests
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("z", type=int, help="Zoom level")
    parser.add_argument("x", type=int, help="Tile column")
    parser.add_argument("y", type=int, help="Tile row")
    parser.add_argument("--output", default=Path("tile.png"), type=Path, help="Output PNG path")
    args = parser.parse_args()
    main(args.z, args.x, args.y, args.output)
