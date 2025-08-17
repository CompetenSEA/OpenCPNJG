"""Lookup table and helpers for mapping SCAMIN to zoom ranges."""
from __future__ import annotations
from typing import Dict, Optional, Tuple

SCAMIN_ZOOM_MAP: Dict[int, int] = {
    50000000: 0,
    20000000: 2,
    12000000: 3,
    6000000: 4,
    3000000: 5,
    1500000: 6,
    700000: 7,
    350000: 8,
    180000: 9,
    90000: 10,
    45000: 11,
    22000: 12,
    12000: 13,
    8000: 14,
    4000: 15,
    2000: 16,
}


def scamin_to_zoom(scamin: Optional[float], mapping: Dict[int, int] = SCAMIN_ZOOM_MAP) -> int:
    """Return the WebMercator zoom level for an S-57 ``SCAMIN`` value."""
    if scamin is None:
        return 0
    try:
        scamin_val = float(scamin)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return 0
    for scale in sorted(mapping.keys(), reverse=True):
        if scamin_val >= scale:
            return mapping[scale]
    return max(mapping.values())


def zoom_limits(scamin: Optional[float]) -> Tuple[int, int]:
    """Return ``(minzoom, maxzoom)`` for the supplied ``SCAMIN``."""
    minzoom = scamin_to_zoom(scamin)
    return minzoom, minzoom + 2

__all__ = ["scamin_to_zoom", "zoom_limits", "SCAMIN_ZOOM_MAP"]
