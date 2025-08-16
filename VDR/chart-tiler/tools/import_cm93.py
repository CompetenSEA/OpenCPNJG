from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple

try:
    from .import_enc import import_dir  # type: ignore
except Exception:  # pragma: no cover
    from import_enc import import_dir  # type: ignore


def import_tree(src: Path) -> Tuple[Path, Path]:
    cli = os.environ.get("OPENCN_CM93_CLI")
    if not cli:
        print("SKIP: OPENCN_CM93_CLI not set", file=sys.stderr)
        return (Path(), Path())
    with tempfile.TemporaryDirectory() as tmp:
        enc_dir = Path(tmp) / "enc"
        enc_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([cli, "--in", str(src), "--out", str(enc_dir)], check=True)
        return import_dir(enc_dir, kind="cm93")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    args = ap.parse_args(argv)
    import_tree(args.src)


if __name__ == "__main__":
    main()
