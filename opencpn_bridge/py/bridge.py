"""Python wrappers around the stub OpenCPN bridge."""
from __future__ import annotations

from . import opencpn_bridge as _bridge


def build_senc(chart_path: str, output_dir: str) -> str:
    """Create a stub SENC and return the output directory."""
    return _bridge.build_senc(chart_path, output_dir)


def query_tile_mvt(senc_root: str, z: int, x: int, y: int) -> bytes:
    """Return an empty Mapbox Vector Tile for the given coordinates."""
    return _bridge.query_tile_mvt(senc_root, z, x, y)

