"""Python wrappers around the OpenCPN bridge.

This module prefers a compiled extension but falls back to lightweight
Python stubs when the extension is unavailable. The stubs mimic the
tileserver contract used by the real bridge.
"""

from __future__ import annotations

import json
from pathlib import Path

# Minimal empty Mapbox Vector Tile with a single layer named ``empty``.
EMPTY_MVT_BYTES = bytes.fromhex("1a0c0a05656d7074792880207802")

try:  # pragma: no cover - exercised via integration tests
    from . import opencpn_bridge as _bridge  # type: ignore
except Exception:  # pragma: no cover - extension missing
    _bridge = None


if _bridge is not None:
    build_senc = _bridge.build_senc
    query_tile_mvt = _bridge.query_tile_mvt
else:

    def build_senc(
        dataset_root: str,
        out_dir: str,
        *,
        bounds: tuple[float, float, float, float] | None = None,
        minzoom: int | None = None,
        maxzoom: int | None = None,
    ) -> str:
        """Create a stub SENC and return a fake handle path."""
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        provenance = {
            "dataset_root": dataset_root,
            "bounds": bounds,
            "minzoom": minzoom,
            "maxzoom": maxzoom,
        }
        (out / "provenance.json").write_text(json.dumps(provenance))
        return str(out / "handle.fake")

    def query_tile_mvt(
        senc_root: str,
        z: int,
        x: int,
        y: int,
    ) -> tuple[bytes, str, bool]:
        """Return a minimal empty Mapbox Vector Tile."""
        return (EMPTY_MVT_BYTES, "", False)

