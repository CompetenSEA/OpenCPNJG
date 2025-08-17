"""Pure Python implementation of the chart tiler bindings."""

from __future__ import annotations

import os
import sys
from typing import Dict
from collections.abc import Sequence

# Ensure the Python charts library is importable when running from the
# source tree.  The module lives in ``VDR/opencpn-libs/py`` relative to
# this file.
_LIB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "opencpn-libs", "py")
)
if _LIB_PATH not in sys.path:
    sys.path.append(_LIB_PATH)

import charts as _charts


def load_cell(path: str) -> None:
    """Delegate to :func:`charts.load_cell`."""
    _charts.load_cell(path)


def generate_tile(bbox: Sequence[float], z: int, options: dict[str, object] | None = None) -> bytes:
    """Render a chart tile.

    Parameters mirror the original pybind11 extension.  Depending on the
    requested format either a PNG image or a small Mapbox Vector Tile is
    returned.
    """
    options = options or {}
    fmt = options.get("format", "png")
    palette = options.get("palette", "day")
    safety = float(options.get("safetyContour", 0.0))

    if fmt not in {"png", "mvt"}:
        raise ValueError("format must be 'png' or 'mvt'")
    if palette not in {"day", "dusk", "night"}:
        raise ValueError("palette must be 'day', 'dusk', or 'night'")

    minx, miny, maxx, maxy = bbox
    if fmt == "png":
        return _charts.render_tile_png(minx, miny, maxx, maxy, z, palette)
    return _charts.render_tile_mvt(minx, miny, maxx, maxy, z, safety)
