from __future__ import annotations

"""Convert simple CSV sounding data to GeoJSON and GeoPackage."""

import argparse
import csv
import json
import sqlite3
from pathlib import Path
from typing import List, Tuple
from collections.abc import Iterable

Feature = tuple[int, str]


def load_csv(file: Path, geom_type: str) -> list[Feature]:
    feats: list[Feature] = []
    if not file.exists():
        return feats
    with file.open() as fh:
        reader = csv.reader(fh)
        for idx, row in enumerate(reader, 1):
            try:
                nums = [float(tok) for tok in row]
            except ValueError:
                nums = [0.0 for _ in row]
            geom = None
            if geom_type == "Point" and len(nums) >= 2:
                geom = {"type": "Point", "coordinates": [nums[0], nums[1]]}
            elif geom_type == "LineString" and len(nums) >= 4:
                geom = {
                    "type": "LineString",
                    "coordinates": [[nums[0], nums[1]], [nums[2], nums[3]]],
                }
            elif geom_type == "Polygon" and len(nums) >= 6:
                geom = {
                    "type": "Polygon",
                    "coordinates": [
                        [[nums[0], nums[1]], [nums[2], nums[3]], [nums[4], nums[5]]]
                    ],
                }
            if geom:
                feat = {"type": "Feature", "geometry": geom, "properties": {"id": idx}}
                feats.append((idx, json.dumps(feat)))
    return feats


def write_geojson(file: Path, feats: Iterable[Feature]) -> None:
    collection = {
        "type": "FeatureCollection",
        "features": [json.loads(gj) for _, gj in feats],
    }
    with file.open("w") as fh:
        json.dump(collection, fh)


def write_gpkg(file: Path, table: str, feats: Iterable[Feature]) -> None:
    db = sqlite3.connect(file)
    cur = db.cursor()
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {table}(id INTEGER PRIMARY KEY, geojson TEXT)"
    )
    cur.executemany(f"INSERT INTO {table}(id, geojson) VALUES (?, ?)", feats)
    db.commit()
    db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args(argv)
    if args.schema != "vdr":
        parser.error("only --schema vdr is supported")

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pts = load_csv(src / "pts.csv", "Point")
    ln = load_csv(src / "ln.csv", "LineString")
    ar = load_csv(src / "ar.csv", "Polygon")

    write_geojson(out / "pts.geojson", pts)
    write_geojson(out / "ln.geojson", ln)
    write_geojson(out / "ar.geojson", ar)

    gpkg = out / "cm93.gpkg"
    write_gpkg(gpkg, "cm93_pts", pts)
    write_gpkg(gpkg, "cm93_ln", ln)
    write_gpkg(gpkg, "cm93_ar", ar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
