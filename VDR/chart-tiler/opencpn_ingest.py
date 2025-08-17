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

from opencpn_bridge import build_senc
from registry import get_registry

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "senc"


def ingest(source: Path, dataset_id: str, chart_type: str = "s57") -> Path:
    """Create chart cache from *source* and register it.

    ``chart_type`` may be ``"s57"`` or ``"cm93"`` and determines the
    registry entry and file suffix used for the cached artefact.
    """

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    if chart_type == "cm93":
        out_path = ASSETS_DIR / f"{dataset_id}.cm93"
        build_senc(str(source), chart_type)
        out_path.write_text("cm93")
        meta_path = out_path.with_suffix(".cm93.json")
        meta = {"id": dataset_id, "bbox": [0, 0, 0, 0], "scale_min": 0, "scale_max": 0}
        meta_path.write_text(json.dumps(meta))
        registry = get_registry()
        registry.register_cm93(meta_path, out_path)
        return out_path

    # Default S57/ENC path
    senc_path = ASSETS_DIR / f"{dataset_id}.senc"
    build_senc(str(source), chart_type)
    senc_path.write_text("senc")
    meta = {"id": dataset_id, "bbox": [0, 0, 0, 0], "scale_min": 0, "scale_max": 0}
    meta_path = senc_path.with_name(f"{senc_path.stem}.senc.json")
    meta_path.write_text(json.dumps(meta))
    registry = get_registry()
    registry.register_senc(meta_path, senc_path)
    return senc_path


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to chart source")
    parser.add_argument("dataset_id", type=str, help="Dataset identifier")
    parser.add_argument("--type", choices=["s57", "cm93"], default="s57", help="Chart type")
    args = parser.parse_args()
    ingest(args.source, args.dataset_id, chart_type=args.type)
