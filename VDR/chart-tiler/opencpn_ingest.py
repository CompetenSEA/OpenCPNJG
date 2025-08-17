from __future__ import annotations

"""Build an OpenCPN SENC cache and register it.

Usage
-----
>>> python opencpn_ingest.py SOURCE DATASET_ID

``SOURCE`` is the path to an ENC dataset.  The resulting ``DATASET_ID`` is
used for the output ``.senc`` cache and registry entry.
"""

import json
from pathlib import Path

from opencpn_bridge import build_senc, query_features
from registry import get_registry

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "senc"


def ingest(source: Path, dataset_id: str) -> Path:
    """Create SENC cache from *source* and register it."""

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    senc_path = ASSETS_DIR / f"{dataset_id}.senc"
    build_senc(str(source), str(senc_path))
    info = query_features(str(senc_path))
    bbox = info.get("bbox", [0, 0, 0, 0])
    scale_min = int(info.get("scale_min", 0))
    scale_max = int(info.get("scale_max", 0))
    meta = {
        "id": dataset_id,
        "bbox": bbox,
        "scale_min": scale_min,
        "scale_max": scale_max,
    }
    meta_path = senc_path.with_name(f"{senc_path.stem}.senc.json")
    meta_path.write_text(json.dumps(meta))
    registry = get_registry()
    registry.register_senc(meta_path, senc_path)
    return senc_path


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to ENC source")
    parser.add_argument("dataset_id", type=str, help="Dataset identifier")
    args = parser.parse_args()
    ingest(args.source, args.dataset_id)
