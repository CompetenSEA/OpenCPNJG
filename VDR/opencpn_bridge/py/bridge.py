"""Python wrappers around the OpenCPN bridge.

The native :mod:`opencpn_bridge` extension is optional.  When it cannot be
imported, lightweight stub implementations are provided so that other parts of
the package can operate in environments where the extension is unavailable.

All public functions return a three-tuple ``(data, etag, compressed)``:

* ``data`` is the requested payload, such as a SENC handle path or tile bytes.
* ``etag`` is an optional identifier for the payload, ``None`` if unknown.
* ``compressed`` signals if ``data`` is already gzip compressed.
"""

from __future__ import annotations

import json
from pathlib import Path

# Minimal empty Mapbox Vector Tile with a single layer named "empty".
_EMPTY_MVT = bytes.fromhex("1a0c0a05656d7074792880207802")

try:  # pragma: no cover - exercised when the native module is present
    import opencpn_bridge as _bridge  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - module missing or failed to import
    _bridge = None

    def build_senc(dataset_root: str, out_dir: str) -> tuple[str, None, bool]:
        """Create a stub SENC and return a fake handle path.

        A minimal ``provenance.json`` file is written to ``out_dir`` recording
        ``dataset_root``.  The returned tuple contains the fake handle path,
        ``None`` for the ETag and ``False`` to indicate the data is not
        compressed.
        """

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "provenance.json").write_text(
            json.dumps({"dataset_root": dataset_root})
        )
        handle = str(out / "handle.fake")
        return handle, None, False

    def query_tile_mvt(
        senc_root: str,
        z: int,
        x: int,
        y: int,
    ) -> tuple[bytes, None, bool]:
        """Return a tiny, valid but empty Mapbox Vector Tile."""

        return _EMPTY_MVT, None, False

else:  # pragma: no cover - exercised when the native module is available
    # Expose the native implementations directly.
    build_senc = _bridge.build_senc  # type: ignore[attr-defined]
    query_tile_mvt = _bridge.query_tile_mvt  # type: ignore[attr-defined]

