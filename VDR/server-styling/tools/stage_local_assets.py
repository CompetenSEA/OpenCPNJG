#!/usr/bin/env python3
"""Stage S-52/S-57 assets from a repo-local data directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ASSETS = [
    "chartsymbols.xml",
    "rastersymbols-day.png",
    "S52RAZDS.RLE",
    "s57objectclasses.csv",
    "s57attributes.csv",
    "attdecode.csv",
]


def _hash_path(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def stage_assets(repo_data: Path, dest: Path, force: bool) -> dict[str, str]:
    manifest: dict[str, str] = {}
    dest.mkdir(parents=True, exist_ok=True)
    for name in ASSETS:
        src = repo_data / name
        if not src.exists():
            continue
        dst = dest / name
        if dst.exists() and not force:
            if dst.read_bytes() == src.read_bytes():
                manifest[name] = _hash_path(dst)
                continue
        shutil.copy2(src, dst)
        manifest[name] = _hash_path(dst)
    if manifest:
        (dest / "assets.manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True)
        )
    return manifest


def main() -> int:  # pragma: no cover - CLI helper
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-data", type=Path, required=True)
    p.add_argument("--dest", type=Path, required=True)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    manifest = stage_assets(args.repo_data, args.dest, args.force)
    print(f"Staged {len(manifest)} assets" if manifest else "No assets staged")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI helper
    raise SystemExit(main())
