#!/usr/bin/env python3
"""Stage a minimal set of OpenCPN S-52/S-57 assets."""

from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
from typing import Dict

ASSETS = [
    "chartsymbols.xml",
    "rastersymbols-day.png",
    "S52RAZDS.RLE",
    "s57objectclasses.csv",
    "s57attributes.csv",
    "attdecode.csv",
]

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def stage_assets(repo_data: Path, dest: Path, force: bool = False) -> Dict[str, str]:
    repo_data, dest = Path(repo_data), Path(dest)
    missing = [n for n in ASSETS if not (repo_data / n).is_file()]
    if missing:
        raise FileNotFoundError("missing assets in repo: " + ", ".join(sorted(missing)))
    if dest.exists():
        if force: shutil.rmtree(dest)
        else: raise FileExistsError(f"{dest} exists; use --force to overwrite")
    dest.mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, str] = {}
    for name in ASSETS:
        src, dst = repo_data / name, dest / name
        shutil.copy2(src, dst)
        manifest[name] = _sha256(dst)
    (dest / "assets.manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-data", type=Path, required=True)
    p.add_argument("--dest", type=Path, required=True)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    manifest = stage_assets(args.repo_data, args.dest, args.force)
    print(f"Staged {len(manifest)} assets")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
