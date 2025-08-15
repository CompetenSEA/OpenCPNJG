"""Synchronise OpenCPN S-52 assets.

The script uses a lock file to pin the upstream OpenCPN repository commit
containing the S-52 data files. Alternatively a local source directory may be
provided via ``--local-src`` to avoid network access during development. Only a
minimal set of text assets are copied into the destination directory and a
manifest of their sizes and SHA256 hashes is produced. Binary artefacts
(PNG/RLE/CSV) are intentionally not committed to version control; they are
downloaded at build time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "chartsymbols.xml",
    "rastersymbols-day.png",
    "S52RAZDS.RLE",
    "s57objectclasses.csv",
    "s57attributes.csv",
    "attdecode.csv",
}


def _parse_lock(lock_path: Path) -> dict[str, str]:
    """Read ``repo``, ``path`` and ``commit`` keys from a lock file."""

    data: dict[str, str] = {}
    for line in lock_path.read_text().splitlines():
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


def _copy_required(src_dir: Path, dest_dir: Path) -> dict[str, dict[str, int | str]]:
    """Copy required files from ``src_dir`` to ``dest_dir`` and build a manifest."""

    manifest: dict[str, dict[str, int | str]] = {}
    for name in sorted(REQUIRED_FILES):
        src = src_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Required asset '{name}' missing in upstream repo")
        dst = dest_dir / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest[name] = {"size": dst.stat().st_size, "sha256": _sha256(dst)}
    return manifest


def main() -> None:  # pragma: no cover - thin CLI wrapper
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True, help="Path to lock file")
    parser.add_argument(
        "--dest", type=Path, required=True, help="Destination directory for assets"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite destination if it exists"
    )
    parser.add_argument(
        "--local-src",
        type=Path,
        help="Copy assets from a local OpenCPN data directory instead of cloning",
    )
    args = parser.parse_args()

    if args.dest.exists() and not args.force:
        raise SystemExit(f"Destination {args.dest} exists; use --force to overwrite")

    args.dest.mkdir(parents=True, exist_ok=True)

    if args.local_src:
        src_base = args.local_src
        if not src_base.exists():
            raise FileNotFoundError(f"Local source '{src_base}' not found")
        manifest = _copy_required(src_base, args.dest)
    else:
        lock = _parse_lock(args.lock)
        repo = lock["repo"]
        repo_path = lock["path"].strip("/")
        commit = lock["commit"]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            subprocess.run(["git", "init", tmpdir], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(
                ["git", "-C", tmpdir, "remote", "add", "origin", repo],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                ["git", "-C", tmpdir, "fetch", "--depth", "1", "origin", commit],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                ["git", "-C", tmpdir, "checkout", commit],
                check=True,
                stdout=subprocess.DEVNULL,
            )

            src_base = tmp / repo_path
            if not src_base.exists():
                raise FileNotFoundError(f"Path '{repo_path}' not found in repo")

            manifest = _copy_required(src_base, args.dest)

    manifest_path = args.dest / "assets.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"Wrote manifest with {len(manifest)} entries to {manifest_path}")


if __name__ == "__main__":
    main()

