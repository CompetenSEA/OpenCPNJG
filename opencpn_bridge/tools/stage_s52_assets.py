#!/usr/bin/env python3
"""Stage OpenCPN S-52/S-57 assets for opencpn_bridge."""

from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
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


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "data" / "s57data"
    dest = repo_root / "opencpn_bridge" / "dist" / "assets" / "s52"
    dest.mkdir(parents=True, exist_ok=True)

    missing = [name for name in ASSETS if not (src / name).is_file()]
    if missing:
        raise FileNotFoundError("missing assets: " + ", ".join(sorted(missing)))

    manifest: dict[str, str] = {}
    for name in ASSETS:
        shutil.copy2(src / name, dest / name)
        manifest[name] = _sha256(dest / name)

    (dest / "assets.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    try:
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        url = "unknown"
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    (dest / "PROVENANCE.txt").write_text(
        f"Upstream: {url}\nCommit: {commit}\n", encoding="utf-8"
    )

    print(f"Staged {len(manifest)} assets to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
