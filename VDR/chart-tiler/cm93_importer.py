"""CM93 importer applying regional offsets."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List

from shapely.geometry import shape, mapping
from shapely.affinity import translate


OffsetDict = Dict[str, tuple[float, float]]


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
