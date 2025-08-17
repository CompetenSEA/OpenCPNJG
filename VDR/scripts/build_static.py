#!/usr/bin/env python3
"""Build static CAS assets and manifest.

This script gathers selected runtime assets and copies them into
`VDR/static/cas` using SHA256 content addressed filenames.  A manifest
mapping logical keys to the hashed filenames is written along with a
PROVENANCE.txt file listing upstream commit SHAs with SPDX license
identifiers.

The script may be extended as additional assets are required.  Missing
assets are skipped so it is safe to run in partial environments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Iterable

ROOT = Path(__file__).resolve().parent.parent
CAS_DIR = ROOT / "static" / "cas"
MANIFEST_PATH = CAS_DIR / "manifest.json"
PROVENANCE_PATH = CAS_DIR / "PROVENANCE.txt"

# Logical asset name -> relative path
DEFAULT_ASSETS = {
    "dict.json": ROOT / "server-styling" / "dist" / "dict.json",
    "sprite.png": ROOT / "server-styling" / "dist" / "sprite.png",
    "sprite.json": ROOT / "server-styling" / "dist" / "sprite.json",
}

# Glyph ranges commonly used by maplibre; these are optional and will be
# included if present.
GLYPH_DIR = ROOT / "server-styling" / "dist" / "glyphs"
GLYPH_RANGES = ["0-255.pbf", "256-511.pbf", "512-767.pbf", "768-1023.pbf"]

# Upstream provenance directories and SPDX license identifiers
PROVENANCE_SOURCES = [
    (ROOT / "server-styling", "GPL-2.0-or-later"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_assets(assets: Dict[str, Path]) -> Dict[str, str]:
    CAS_DIR.mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, str] = {}
    for logical, src in assets.items():
        if not src.exists():
            continue
        digest = sha256_file(src)
        dest_name = f"{digest}{src.suffix}"
        dest = CAS_DIR / dest_name
        shutil.copy2(src, dest)
        manifest[logical] = dest_name
    return manifest


def gather_assets() -> Dict[str, Path]:
    assets = dict(DEFAULT_ASSETS)
    if GLYPH_DIR.exists():
        for name in GLYPH_RANGES:
            p = GLYPH_DIR / name
            if p.exists():
                assets[f"glyphs/{name}"] = p
    return assets


def write_manifest(manifest: Dict[str, str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")


def write_provenance() -> None:
    lines: Iterable[str] = []
    for path, spdx in PROVENANCE_SOURCES:
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=path, text=True
            ).strip()
        except subprocess.CalledProcessError:
            continue
        lines.append(f"{path.name} {sha} SPDX-License-Identifier: {spdx}\n")
    PROVENANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PROVENANCE_PATH.open("w", encoding="utf-8") as fh:
        fh.writelines(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static CAS assets")
    parser.add_argument(
        "--clean", action="store_true", help="Remove previous CAS output first"
    )
    args = parser.parse_args()

    if args.clean and CAS_DIR.exists():
        shutil.rmtree(CAS_DIR)

    assets = gather_assets()
    manifest = build_assets(assets)
    write_manifest(manifest)
    write_provenance()
    print(f"Wrote {len(manifest)} assets to {CAS_DIR}")


if __name__ == "__main__":
    main()
