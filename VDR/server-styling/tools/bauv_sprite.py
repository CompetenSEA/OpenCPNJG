"""Rasterise BAUV SVG symbols into a MapLibre sprite sheet.

The script expects the BAUV assets to be vendored under ``VDR/BAUV`` and uses
``resvg`` to convert individual SVGs into PNGs.  The generated sprite and JSON
manifest are written to ``dist/sprites`` using the prefix ``bauv``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "third_party"))

import bauv_adapter


def _rasterise(svg: Path, png: Path) -> None:
    """Render ``svg`` to ``png`` using the ``resvg`` command line tool."""
    subprocess.run(["resvg", str(svg), str(png)], check=True)


def build_sprite(symbols: List[str], out_base: Path) -> None:
    tmpdir = Path(tempfile.mkdtemp())
    images: List[tuple[str, Image.Image]] = []
    for name in symbols:
        svg = bauv_adapter.symbol_path(name)
        png = tmpdir / f"{name}.png"
        _rasterise(svg, png)
        images.append((name, Image.open(png)))

    width = sum(img.width for _, img in images)
    height = max((img.height for _, img in images), default=0)
    sprite = Image.new("RGBA", (width, height))
    manifest: Dict[str, Dict[str, int]] = {}
    x = 0
    for name, img in images:
        sprite.paste(img, (x, 0))
        manifest[name] = {
            "x": x,
            "y": 0,
            "width": img.width,
            "height": img.height,
            "pixelRatio": 1,
        }
        x += img.width

    out_base.parent.mkdir(parents=True, exist_ok=True)
    sprite.save(out_base.with_suffix(".png"))
    with out_base.with_suffix(".json").open("w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2, sort_keys=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("symbols", nargs="+", help="BAUV symbol names to rasterise")
    p.add_argument(
        "--out-base",
        type=Path,
        default=ROOT / "dist" / "sprites" / "bauv",
        help="Output path prefix for sprite files",
    )
    args = p.parse_args()
    build_sprite(args.symbols, args.out_base)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
