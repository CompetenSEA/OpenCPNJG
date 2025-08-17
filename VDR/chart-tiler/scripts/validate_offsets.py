"""Validate continuity of CM93 cell offsets."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List

from shapely.geometry import shape
from shapely.affinity import translate


def _load_offsets(path: Path) -> Dict[str, tuple[float, float]]:
    offs: Dict[str, tuple[float, float]] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            offs[row["cell_id"]] = (float(row["offset_dx_m"]), float(row["offset_dy_m"]))
    return offs


def _apply(geom, dx: float, dy: float):
    return translate(geom, xoff=dx, yoff=dy)


def validate(features: List[Dict[str, object]], offsets: Dict[str, tuple[float, float]], tolerance: float = 1e-6) -> bool:
    geoms = [shape(f["geometry"]) for f in features]
    cells = [str(f.get("properties", {}).get("cell_id", f.get("cell_id"))) for f in features]

    # distance before applying offsets
    pre = geoms[0].boundary.distance(geoms[1].boundary)

    post_geoms = []
    for g, cid in zip(geoms, cells):
        dx, dy = offsets.get(cid, (0.0, 0.0))
        post_geoms.append(_apply(g, dx, dy))

    post = post_geoms[0].boundary.distance(post_geoms[1].boundary)
    return pre >= post and post <= tolerance


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Validate CM93 offsets")
    parser.add_argument("features", help="GeoJSON features file")
    parser.add_argument("--offsets", required=True, help="Offsets CSV")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args()

    import json

    feats = json.loads(Path(args.features).read_text())["features"]
    offs = _load_offsets(Path(args.offsets))
    ok = validate(feats, offs, args.tolerance)
    if not ok:
        raise SystemExit("offset continuity check failed")


if __name__ == "__main__":  # pragma: no cover
    main()
