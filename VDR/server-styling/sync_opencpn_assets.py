#!/usr/bin/env python3
"""Fetch S-52 assets from the OpenCPN repository at a pinned commit.

The repository/commit/path are read from ``opencpn-assets.lock``.  Only the
required files are copied into ``opencpn-assets/`` and their size and sha256
checksums are verified after copy.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

LOCK_FILE = Path(__file__).with_name("opencpn-assets.lock")
TARGET_DIR = Path(__file__).with_name("opencpn-assets")

REQUIRED_FILES = {
    "chartsymbols.xml",
    "rastersymbols-day.png",
    "S52RAZDS.RLE",
}


def _parse_lock() -> dict[str, str]:
    data: dict[str, str] = {}
    for line in LOCK_FILE.read_text().splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition("=")
        data[key.strip()] = value.strip()
    missing = {k for k in ("repo", "path", "commit") if k not in data}
    if missing:
        raise ValueError(f"Missing keys in lock file: {', '.join(sorted(missing))}")
    return data


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    lock = _parse_lock()
    repo = lock["repo"]
    repo_path = lock["path"].strip("/")
    commit = lock["commit"]

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Fetch only the required commit depth-one
        subprocess.run(["git", "init", tmpdir], check=True)
        subprocess.run(["git", "-C", tmpdir, "remote", "add", "origin", repo], check=True)
        subprocess.run(["git", "-C", tmpdir, "fetch", "--depth", "1", "origin", commit], check=True)
        subprocess.run(["git", "-C", tmpdir, "checkout", commit], check=True)

        src_base = tmp / repo_path
        if not src_base.exists():
            raise FileNotFoundError(f"Path '{repo_path}' not found in repo")

        files = set(REQUIRED_FILES)
        files.update(p.name for p in src_base.glob("*.csv"))

        for name in sorted(files):
            src = src_base / name
            if not src.exists():
                raise FileNotFoundError(f"Required asset '{name}' missing in upstream repo")
            dst = TARGET_DIR / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if src.stat().st_size != dst.stat().st_size:
                raise RuntimeError(f"Size mismatch for '{name}'")
            if _sha256(src) != _sha256(dst):
                raise RuntimeError(f"Hash mismatch for '{name}'")
            print(f"Fetched {name} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
