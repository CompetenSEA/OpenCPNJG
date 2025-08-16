#!/usr/bin/env python3
"""Stage a minimal set of OpenCPN S‑52/S‑57 assets.

This helper copies a handful of binary assets from the repository checkout
into a build directory.  A JSON manifest containing SHA‑256 checksums is
written alongside the files which allows downstream build steps to verify the
contents without shipping the binaries in Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict


# Filenames relative to the ``data/s57data`` directory in the repository.
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
    """Copy assets from ``repo_data`` into ``dest``.

    :param repo_data: Path to the ``data/s57data`` directory in the OpenCPN
        repository.
    :param dest: Destination directory for staged assets.
    :param force: Overwrite ``dest`` if it already exists.
    :returns: Mapping of filenames to SHA‑256 checksums.
    :raises FileNotFoundError: if any required asset is missing.
    :raises FileExistsError: if ``dest`` exists and ``force`` is ``False``.
    """

    repo_data = Path(repo_data)
    dest = Path(dest)

    missing = [name for name in ASSETS if not (repo_data / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "missing assets in repo: " + ", ".join(sorted(missing))
        )

    if dest.exists():
        if force:
            shutil.rmtree(dest)
        else:
            raise FileExistsError(f"{dest} exists; use --force to overwrite")

    dest.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, str] = {}
    for name in ASSETS:
        src = repo_data / name
        dst = dest / name
        shutil.copy2(src, dst)
        manifest[name] = _sha256(dst)

    (dest / "assets.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest


def main() -> int:  # pragma: no cover - CLI helper
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-data", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    manifest = stage_assets(args.repo_data, args.dest, args.force)
    print(f"Staged {len(manifest)} assets")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI helper
    raise SystemExit(main())

