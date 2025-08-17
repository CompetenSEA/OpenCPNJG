"""Python wrappers around the OpenCPN bridge."""
from __future__ import annotations

from . import opencpn_bridge as _bridge


def build_senc(chart_path: str, output_dir: str) -> str:
    """Create a SENC and return the output directory."""
    return _bridge.build_senc(chart_path, output_dir)


def query_tile_mvt(senc_root: str, z: int, x: int, y: int) -> bytes:
    """Return an MVT tile for the given chart handle."""
    return _bridge.query_tile_mvt(senc_root, z, x, y)
