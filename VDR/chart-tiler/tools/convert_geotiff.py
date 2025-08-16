#!/usr/bin/env python3
"""Convert a GeoTIFF into a Cloud Optimized GeoTIFF (COG).

The script is a light wrapper around ``gdal_translate`` and ``gdalinfo``.  It
creates the COG with internal overviews and writes a small JSON sidecar with
basic spatial metadata.  Re‑running the command is idempotent – if the input
file checksum matches the one recorded in the sidecar the conversion is
skipped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "geotiff"
DATA_DIR.mkdir(parents=True, exist_ok=True)

GDAL_TRANSLATE_OPTS = [
    "-of", "COG",
    "-co", "COMPRESS=LZW",
    "-co", "BIGTIFF=IF_NEEDED",
    "-co", "BLOCKSIZE=512",
    "-co", "RESAMPLING=AVERAGE",
    "-co", "OVERVIEWS=IGNORE_EXISTING",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_gdalinfo(text: str) -> Dict[str, Any]:
    """Very small parser for the bits of gdalinfo we care about."""
    bbox: List[float] = []
    epsg = None
    res: List[float] = []
    overviews: List[int] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Upper Left"):
            parts = line.split("(")[1].split(")")[0].split(",")
            ulx, uly = map(float, parts)
            bbox = [ulx, 0, 0, uly]
        elif line.startswith("Lower Right") and bbox:
            parts = line.split("(")[1].split(")")[0].split(",")
            lrx, lry = map(float, parts)
            bbox[2], bbox[1] = lrx, lry
        elif line.startswith("EPSG"):
            try:
                epsg = int(line.split(":")[1])
            except Exception:
                pass
        elif "Pixel Size" in line:
            parts = line.split("(")[1].split(")")[0].split(",")
            res = [float(parts[0]), float(parts[1])]
        elif line.startswith("Overviews"):
            nums = [int(p.split("x")[0]) for p in line.split(" ") if "x" in p]
            overviews = nums
    return {"bbox": bbox, "epsg": epsg, "resolution": res, "overviews": overviews}


def convert(path: Path) -> Path:
    """Convert ``path`` to a COG if needed and return output path."""
    assert path.exists(), f"{path} missing"
    out = DATA_DIR / f"{path.stem}.cog.tif"
    sidecar = out.with_suffix(".json")
    digest = sha256(path)
    if sidecar.exists():
        try:
            info = json.loads(sidecar.read_text())
            if info.get("checksum") == digest and out.exists():
                return out
        except Exception:
            pass
    # Build COG
    cmd = ["gdal_translate", *GDAL_TRANSLATE_OPTS, str(path), str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    # Gather metadata
    info_cmd = ["gdalinfo", str(out)]
    proc = subprocess.run(info_cmd, check=True, capture_output=True, text=True)
    meta = parse_gdalinfo(proc.stdout)
    meta["checksum"] = digest
    sidecar.write_text(json.dumps(meta, indent=2))
    return out


def main(argv: List[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tiff", type=Path, help="Input GeoTIFF")
    args = ap.parse_args(argv)
    convert(args.tiff)


if __name__ == "__main__":
    main()
