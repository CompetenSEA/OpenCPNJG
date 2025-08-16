from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple

from registry import get_registry

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "mbtiles"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ATTRS = [
    "OBJL",
    "DRVAL1",
    "DRVAL2",
    "VALDCO",
    "VALSOU",
    "QUAPOS",
    "WATLEV",
    "CATWRK",
    "CATOBS",
    "SCAMIN",
    "OBJNAM",
    "NOBJNM",
]


def _sha256(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        with p.open("rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()


def _have_tools() -> bool:
    import shutil

    return shutil.which("ogr2ogr") and shutil.which("tippecanoe")


def import_dir(
    src: Path,
    *,
    name: str | None = None,
    respect_scamin: bool = False,
    minzoom: int = 0,
    maxzoom: int = 16,
    tmpdir: Path | None = None,
    keep_temp: bool = False,
    kind: str = "enc",
) -> Tuple[Path, Path]:
    """Ingest S-57 cells from ``src`` into an MBTiles dataset."""

    src = Path(src)
    cells = sorted([p for p in src.glob("*.0??")])
    if not cells:
        raise FileNotFoundError("no ENC cells found")
    digest = _sha256(cells)
    chart_name = name or src.name
    mbtiles = DATA_DIR / f"{chart_name}.mbtiles"
    meta_path = DATA_DIR / f"{chart_name}.meta.json"
    if mbtiles.exists() and meta_path.exists():
        try:
            info = json.loads(meta_path.read_text())
            if info.get("sha256") == digest:
                return meta_path, mbtiles
        except Exception:
            pass
    if not _have_tools():
        print("SKIP: ogr2ogr or tippecanoe missing", file=sys.stderr)
        return meta_path, mbtiles
    tmpctx = tempfile.TemporaryDirectory(dir=tmpdir)
    tmp_path = Path(tmpctx.name)
    ndjson = tmp_path / "features.ndjson"
    for cell in cells:
        cmd = [
            "ogr2ogr",
            "-f",
            "GeoJSONSeq",
            "-append",
            "-skipfailures",
            "-select",
            ",".join(ATTRS),
            str(ndjson),
            str(cell),
        ]
        subprocess.run(cmd, check=True)
    tip_cmd = [
        "tippecanoe",
        "-o",
        str(mbtiles),
        "-l",
        "features",
        "--no-tile-size-limit",
        "--force",
        "--read-parallel",
        "--no-feature-limit",
        "--minimum-zoom",
        str(minzoom),
        "--maximum-zoom",
        str(maxzoom),
        str(ndjson),
    ]
    subprocess.run(tip_cmd, check=True)
    if not keep_temp:
        tmpctx.cleanup()
    bbox = [0.0, 0.0, 0.0, 0.0]
    mz, xz = minzoom, maxzoom
    chart_title = chart_name
    try:
        conn = sqlite3.connect(mbtiles)
        cur = conn.cursor()
        meta = dict(cur.execute("SELECT name,value FROM metadata").fetchall())
        bbox = list(map(float, meta.get("bounds", "0,0,0,0").split(",")))
        mz = int(meta.get("minzoom", mz))
        xz = int(meta.get("maxzoom", xz))
        chart_title = meta.get("name", chart_title)
    finally:
        conn.close()
    info = {
        "kind": kind,
        "name": chart_title,
        "bounds": bbox,
        "minzoom": mz,
        "maxzoom": xz,
        "updatedAt": datetime.utcnow().isoformat(),
        "cells": len(cells),
        "scamin": bool(respect_scamin),
        "sha256": digest,
    }
    meta_path.write_text(json.dumps(info, indent=2))
    reg = get_registry()
    reg.register_mbtiles(meta_path, mbtiles)
    return meta_path, mbtiles


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--name")
    ap.add_argument("--respect-scamin", action="store_true")
    ap.add_argument("--minzoom", type=int, default=0)
    ap.add_argument("--maxzoom", type=int, default=16)
    ap.add_argument("--tmpdir", type=Path)
    ap.add_argument("--keep-temp", action="store_true")
    ap.add_argument("--kind", default="enc")
    args = ap.parse_args(argv)
    import_dir(
        args.src,
        name=args.name,
        respect_scamin=args.respect_scamin,
        minzoom=args.minzoom,
        maxzoom=args.maxzoom,
        tmpdir=args.tmpdir,
        keep_temp=args.keep_temp,
        kind=args.kind,
    )


if __name__ == "__main__":
    main()
