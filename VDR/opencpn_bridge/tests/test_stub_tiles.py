"""Exercise stub ``build_senc`` and ``query_tile_mvt`` helpers."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest


def test_stub_tile_roundtrip(tmp_path: Path) -> None:
    """Build a dummy SENC and request a tile from it.

    The real bridge implementation is backed by a native extension.  When the
    extension is not available (for example in lightweight test environments)
    the test is skipped rather than failing.
    """

    try:
        import opencpn_bridge as bridge  # type: ignore
    except Exception:  # pragma: no cover - module missing
        pytest.skip("opencpn_bridge unavailable")

    build_senc = getattr(bridge, "build_senc", None)
    query_tile_mvt = getattr(bridge, "query_tile_mvt", None)
    if build_senc is None or query_tile_mvt is None:  # pragma: no cover
        pytest.skip("bridge stubs missing")

    chart_path = tmp_path / "demo.000"
    chart_path.write_text("stub")

    senc_root = build_senc(str(chart_path), str(tmp_path / "senc"))

    tile = query_tile_mvt(senc_root, 0, 0, 0)
    if isinstance(tile, tuple):
        data, _tile_hash, compressed = tile
    else:  # legacy interface
        data, compressed = tile, False

    assert data  # non-empty

    if compressed or data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)

    # MVT tiles are protobufs which start with the 0x1a tag for the first layer
    assert data.startswith(b"\x1a")

