from __future__ import annotations

"""Build S-52 raster sprites and colour tables for the vector-first server.

The script reads the S-52 data shipped with the repository and stages
sprite sheets and JSON metadata under ``VDR/assets/s52``.  The input
files come from ``data/s57data`` and are part of the OpenCPN
source tree.
"""

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from s52_xml import parse_palette_colors, parse_symbols

REPO_ROOT = Path(__file__).resolve().parents[2]
S57_ROOT = REPO_ROOT / "data" / "s57data"
DEFAULT_CHARTSYMBOLS = S57_ROOT / "chartsymbols.xml"
DEFAULT_OUTPUT = REPO_ROOT / "VDR" / "assets" / "s52"

# Mapping of short palette name -> (colour table name, raster PNG)
PALETTES: dict[str, tuple[str, str]] = {
    "day": ("DAY_BRIGHT", "rastersymbols-day.png"),
    "dusk": ("DUSK", "rastersymbols-dusk.png"),
    "dark": ("NIGHT", "rastersymbols-dark.png"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chartsymbols", type=Path, default=DEFAULT_CHARTSYMBOLS)
    parser.add_argument(
        "--s57data",
        type=Path,
        default=S57_ROOT,
        help="Directory containing rastersymbol PNG files",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def build_assets(chartsymbols: Path, s57data: Path, output: Path) -> None:
    root = ET.parse(chartsymbols).getroot()

    # Build sprite JSON common to all palettes.
    sprites: dict[str, dict[str, int | bool]] = {}
    for name, info in parse_symbols(root).items():
        if not {"x", "y", "w", "h"} <= info.keys():
            continue
        sprites[name] = {
            "x": int(info["x"]),
            "y": int(info["y"]),
            "width": int(info["w"]),
            "height": int(info["h"]),
            "pixelRatio": 1,
            "sdf": False,
        }

    output.mkdir(parents=True, exist_ok=True)

    for short, (palette_name, raster_name) in PALETTES.items():
        # Copy sprite sheet
        src_png = s57data / raster_name
        dst_png = output / raster_name
        shutil.copyfile(src_png, dst_png)

        # Write sprite metadata
        sprite_json = output / f"{Path(raster_name).stem}.json"
        with sprite_json.open("w", encoding="utf-8") as fh:
            json.dump(sprites, fh, indent=2, sort_keys=True)

        # Write colour table
        colours = parse_palette_colors(root, palette_name)
        colour_json = output / f"colors-{short}.json"
        with colour_json.open("w", encoding="utf-8") as fh:
            json.dump(colours, fh, indent=2, sort_keys=True)

        print(f"Wrote assets for {short} palette to {output}")


def main() -> None:  # pragma: no cover - CLI wrapper
    args = parse_args()
    build_assets(args.chartsymbols, args.s57data, args.output)


if __name__ == "__main__":
    main()
