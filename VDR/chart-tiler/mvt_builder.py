from __future__ import annotations

"""Mapbox Vector Tile helpers.

The module provides two helpers:

``encode_mvt``
    Encodes a mapping of layer names to feature iterables.  A plain iterable of
    features is still accepted for backwards compatibility and is encoded in a
    single layer named ``features``.

``fetch_mvt``
    Executes the :func:`enc_mvt` SQL function and concatenates the returned
    layer tiles into a single MVT byte string.
"""

from typing import Iterable, Dict, Any, Mapping, Sequence, Tuple

from mapbox_vector_tile import encode as mvt_encode

try:  # pragma: no cover - optional dependency in tests
    import psycopg2  # type: ignore
except Exception:  # pragma: no cover
    psycopg2 = None  # type: ignore


def encode_mvt(layers: Mapping[str, Iterable[Dict[str, Any]]] | Iterable[Dict[str, Any]]) -> bytes:
    """Encode features into a Mapbox Vector Tile.

    ``layers`` may be a mapping of layer name to iterable of features or an
    iterable of features for the legacy single ``features`` layer.
    """

    if isinstance(layers, Mapping):
        tile_layers = [{"name": name, "features": list(feats)} for name, feats in layers.items()]
    else:  # backwards compatibility
        tile_layers = [{"name": "features", "features": list(layers)}]
    return mvt_encode(tile_layers, extents=4096)


def fetch_mvt(conn, z: int, x: int, y: int) -> bytes:
    """Fetch a pre-encoded tile from PostGIS using enc_mvt(z,x,y).

    ``conn`` must be a ``psycopg2`` connection or compatible object.  Each row
    returned by ``enc_mvt`` contains a layer name and the encoded tile for that
    layer.  The individual layer tiles are concatenated to form the final
    multi-layer tile.
    """

    if psycopg2 is None:  # pragma: no cover - defensive
        raise RuntimeError("psycopg2 not available")

    cur = conn.cursor()
    try:
        cur.execute("SELECT layer, tile FROM enc_mvt(%s,%s,%s)", (z, x, y))
        parts: Sequence[Tuple[str, bytes]] = cur.fetchall()
    finally:
        cur.close()
    return b"".join(tile for _, tile in parts)
