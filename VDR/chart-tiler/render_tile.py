"""Render a single chart tile to PNG for regression tests."""
from __future__ import annotations

import argparse
from pathlib import Path
import math
import charts_py

def tile_bounds(x: int, y: int, z: int) -> list[float]:
    n = 2 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return [lon_left, lat_bottom, lon_right, lat_top]

def main(z: int, x: int, y: int, output: Path) -> None:
    bbox = tile_bounds(x, y, z)
    data = charts_py.generate_tile(bbox, z, fmt="png")
    output.write_bytes(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render a chart tile to PNG")
    parser.add_argument("z", type=int)
    parser.add_argument("x", type=int)
    parser.add_argument("y", type=int)
    parser.add_argument("--output", default="tile.png", type=Path)
    args = parser.parse_args()
    main(args.z, args.x, args.y, args.output)
