from __future__ import annotations

import json
from pathlib import Path

# Minimal empty Mapbox Vector Tile with a single layer named "empty".
_EMPTY_MVT = bytes.fromhex("1a0c0a05656d7074792880207802")

def build_senc(dataset_root: str, out_dir: str) -> str:
    """Create a stub SENC and return a fake handle path.

    A minimal ``provenance.json`` file is written to ``out_dir`` recording
    ``dataset_root``.  The returned handle is a path within ``out_dir`` that
    does not correspond to a real resource.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "provenance.json").write_text(json.dumps({"dataset_root": dataset_root}))
    return str(out / "handle.fake")

def query_tile_mvt(
    handle_or_path: str,
    z: int,
    x: int,
    y: int,
    plane: int,
    safety: int,
    shallow: int,
    deep: int,
) -> bytes:
    """Return a tiny, valid but empty Mapbox Vector Tile."""
    return _EMPTY_MVT
