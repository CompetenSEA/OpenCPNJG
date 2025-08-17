"""CM93 importer applying regional offsets."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import math
import os
import shutil
import sqlite3
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

    cli_env = os.environ.get("OPENCN_CM93_CLI")
    cli: str | None = None
    if cli_env:
        p = Path(cli_env)
        if p.exists():
            cli = str(p)
        else:
            cli = shutil.which(cli_env)
    if not cli:
        cli = shutil.which("cm93_convert")
    if not cli:
        logging.info("cm93_convert not available; falling back to GDAL")
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
    """Apply regional meter offsets to features converting to degrees."""
    adjusted: List[Dict[str, object]] = []
    for feat in features:
        props = feat.get("properties", {})
        cell_id = str(props.get("cell_id", feat.get("cell_id")))
        dx_m, dy_m = offsets.get(cell_id, (0.0, 0.0))
        geom = shape(feat["geometry"])
        lat = geom.centroid.y
        phi = math.radians(lat)
        dx = dx_m / (111_320 * math.cos(phi)) if math.cos(phi) else 0.0
        dy = dy_m / 111_320
        geom = translate(geom, xoff=dx, yoff=dy)
        adj = dict(feat)
        adj["geometry"] = mapping(geom)
        adjusted.append(adj)
    return adjusted


def stream_to_db(
    features: Iterable[Dict[str, object]],
    offsets: OffsetDict,
    conn: sqlite3.Connection,
    *,
    bulk: bool = False,
) -> None:
    """Import adjusted features into ``cm93_*`` tables.

    ``conn`` must provide the required tables.  Existing rows for affected
    cells are removed before insertion so re-imports replace previous data.
    """

    adjusted = apply_offsets(features, offsets)

    pts: List[tuple[int, str]] = []
    ln: List[tuple[int, str]] = []
    ar: List[tuple[int, str]] = []
    labels: List[tuple[int, str, str]] = []
    lights: List[tuple[int, str, str]] = []
    cell_meta: Dict[int, Dict[str, object]] = {}

    for feat in adjusted:
        props = feat.get("properties", {})
        cell_id = int(props.get("cell_id", feat.get("cell_id")))
        geom = shape(feat["geometry"])
        bbox = geom.bounds
        entry = cell_meta.setdefault(
            cell_id,
            {
                "bbox": list(bbox),
                "offset": offsets.get(str(cell_id), (0.0, 0.0)),
                "hash": hashlib.md5(),
            },
        )
        b = entry["bbox"]
        b[0] = min(b[0], bbox[0])
        b[1] = min(b[1], bbox[1])
        b[2] = max(b[2], bbox[2])
        b[3] = max(b[3], bbox[3])
        entry["hash"].update(json.dumps(props, sort_keys=True).encode())

        wkt = geom.wkt
        gtype = geom.geom_type
        if gtype in {"Point", "MultiPoint"}:
            pts.append((cell_id, wkt))
        elif gtype in {"LineString", "MultiLineString"}:
            ln.append((cell_id, wkt))
        elif gtype in {"Polygon", "MultiPolygon"}:
            ar.append((cell_id, wkt))

        text = props.get("text")
        if text:
            labels.append((cell_id, str(text), wkt))
        if props.get("objl") == "LIGHTS":
            lights.append((cell_id, wkt, json.dumps(props, sort_keys=True)))

    cell_ids = list(cell_meta.keys())
    for cid in cell_ids:
        conn.execute("DELETE FROM cm93_pts WHERE cell_id=?", (cid,))
        conn.execute("DELETE FROM cm93_ln WHERE cell_id=?", (cid,))
        conn.execute("DELETE FROM cm93_ar WHERE cell_id=?", (cid,))
        conn.execute("DELETE FROM cm93_labels WHERE cell_id=?", (cid,))
        conn.execute("DELETE FROM cm93_lights WHERE cell_id=?", (cid,))
        conn.execute("DELETE FROM cm93_cells WHERE cell_id=?", (cid,))

    if bulk:
        conn.executemany("INSERT INTO cm93_pts(cell_id, geom) VALUES (?, ?)", pts)
        conn.executemany("INSERT INTO cm93_ln(cell_id, geom) VALUES (?, ?)", ln)
        conn.executemany("INSERT INTO cm93_ar(cell_id, geom) VALUES (?, ?)", ar)
        conn.executemany("INSERT INTO cm93_labels(cell_id, text, geom) VALUES (?, ?, ?)", labels)
        conn.executemany("INSERT INTO cm93_lights(cell_id, geom, attrs) VALUES (?, ?, ?)", lights)
    else:
        for row in pts:
            conn.execute("INSERT INTO cm93_pts(cell_id, geom) VALUES (?, ?)", row)
        for row in ln:
            conn.execute("INSERT INTO cm93_ln(cell_id, geom) VALUES (?, ?)", row)
        for row in ar:
            conn.execute("INSERT INTO cm93_ar(cell_id, geom) VALUES (?, ?)", row)
        for row in labels:
            conn.execute("INSERT INTO cm93_labels(cell_id, text, geom) VALUES (?, ?, ?)", row)
        for row in lights:
            conn.execute("INSERT INTO cm93_lights(cell_id, geom, attrs) VALUES (?, ?, ?)", row)

    for cid, meta in cell_meta.items():
        bbox_str = ",".join(str(v) for v in meta["bbox"])
        dx, dy = meta["offset"]
        meta_hash = meta["hash"].hexdigest()
        conn.execute(
            "INSERT INTO cm93_cells(cell_id, bbox, offset_dx, offset_dy, meta_hash) VALUES (?,?,?,?,?)",
            (cid, bbox_str, dx, dy, meta_hash),
        )
    conn.commit()


def main() -> None:  # pragma: no cover - CLI helper
    parser = argparse.ArgumentParser(description="Import CM93 features with offsets")
    parser.add_argument("input", help="GeoJSON file of features")
    parser.add_argument("--offsets", required=True, help="CSV file with offsets")
    parser.add_argument("--dsn", required=True, help="SQLite database DSN/path")
    parser.add_argument("--bulk", action="store_true", help="Use bulk insertion")
    parser.add_argument("--use-gdal", action="store_true", help="Use ogr2ogr for loading")
    args = parser.parse_args()

    features = json.loads(Path(args.input).read_text())["features"]
    offsets = _load_offsets(Path(args.offsets))
    conn = sqlite3.connect(args.dsn)
    try:
        if args.use_gdal:
            subprocess.check_call(
                [
                    "ogr2ogr",
                    "-f",
                    "SQLite",
                    args.dsn,
                    args.input,
                    "-nln",
                    "cm93_ar",
                ]
            )
        else:
            stream_to_db(features, offsets, conn, bulk=args.bulk)
    finally:
        conn.close()


if __name__ == "__main__":  # pragma: no cover
    main()

__all__ = ["apply_offsets", "run_cm93_convert", "stream_to_db"]
