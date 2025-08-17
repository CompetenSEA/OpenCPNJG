"""CM93 importer applying regional offsets."""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List

from shapely.geometry import shape, mapping
from shapely.affinity import translate


OffsetDict = Dict[str, tuple[float, float]]


def run_cm93_convert(src: Path, out_dir: Path) -> bool:
    """Invoke the optional native ``cm93_convert`` tool.

    Returns ``True`` if the converter was found and executed, ``False``
    otherwise so callers may fall back to GDAL or pre-converted sources.
    """

    cli = shutil.which("cm93_convert")
    if not cli:
        return False
    subprocess.check_call([cli, "--src", str(src), "--out", str(out_dir), "--schema", "vdr"])
    return True


def _load_offsets(path: Path) -> OffsetDict:
    offsets: OffsetDict = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            offsets[row["cell_id"]] = (float(row["offset_dx_m"]), float(row["offset_dy_m"]))
    return offsets


def apply_offsets(features: Iterable[Dict[str, object]], offsets: OffsetDict) -> List[Dict[str, object]]:
    adjusted: List[Dict[str, object]] = []
    for feat in features:
        props = feat.get("properties", {})
        cell_id = str(props.get("cell_id", feat.get("cell_id")))
        dx, dy = offsets.get(cell_id, (0.0, 0.0))
        geom = translate(shape(feat["geometry"]), xoff=dx, yoff=dy)
        adj = dict(feat)
        adj["geometry"] = mapping(geom)
        adjusted.append(adj)
    return adjusted


def main() -> None:  # pragma: no cover - CLI helper
    parser = argparse.ArgumentParser(description="Import CM93 features with offsets")
    parser.add_argument("input", help="GeoJSON file of features")
    parser.add_argument("--offsets", required=True, help="CSV file with offsets")
    parser.add_argument("--output", required=True, help="Output GeoJSON path")
    args = parser.parse_args()

    import json

    features = json.loads(Path(args.input).read_text())
    offsets = _load_offsets(Path(args.offsets))
    adjusted = apply_offsets(features["features"], offsets)
    Path(args.output).write_text(json.dumps({"type": "FeatureCollection", "features": adjusted}))


if __name__ == "__main__":  # pragma: no cover
    main()

__all__ = ["apply_offsets", "run_cm93_convert"]
