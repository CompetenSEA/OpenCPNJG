from __future__ import annotations

"""Simple Mapbox Vector Tile encoder helper."""

from typing import Iterable, Dict, Any

from mapbox_vector_tile import encode as mvt_encode


def encode_mvt(features: Iterable[Dict[str, Any]]) -> bytes:
    """Encode features into a single-layer Mapbox Vector Tile."""

    layer = {"name": "features", "features": list(features)}
    return mvt_encode([layer])
