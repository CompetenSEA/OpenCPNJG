"""Test slippy-map z/x/y <-> bbox conversions."""

from __future__ import annotations

import importlib.util
from pathlib import Path


# ---------------------------------------------------------------------------
# Import the util_bbox module without triggering package side effects.  The
# ``opencpn_bridge.py`` package performs additional imports at module import
# time which fail in the minimal test environment.  Loading the module from its
# file path avoids these circular imports while still exercising the real
# implementation.
# ---------------------------------------------------------------------------
_UTIL_PATH = Path(__file__).resolve().parents[3] / "opencpn_bridge" / "py" / "util_bbox.py"
spec = importlib.util.spec_from_file_location("util_bbox", _UTIL_PATH)
assert spec and spec.loader  # for type checkers
_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_module)  # type: ignore[assignment]
xyz_to_bbox = _module.xyz_to_bbox
bbox_to_xyz = _module.bbox_to_xyz


def test_round_trip_xyz_bbox() -> None:
    """Verify round-trip conversions between tile coordinates and bbox."""

    cases = [
        (0, 0, 0),
        (1, 1, 1),
        (2, 2, 3),
        (5, 11, 22),
        (10, 345, 678),
    ]

    for z, x, y in cases:
        bbox = xyz_to_bbox(z, x, y)
        x2, y2 = bbox_to_xyz(z, *bbox)

        assert (x2, y2) == (x, y)

        west, south, east, north = bbox
        assert west < east
        assert south < north

