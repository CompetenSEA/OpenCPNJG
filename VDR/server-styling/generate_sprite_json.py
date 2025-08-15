"""Generate a MapLibre sprite JSON manifest from ``chartsymbols.xml``.

OpenCPN distributes a large raster atlas (``rastersymbols-day.png``) and an XML
file describing the position of each symbol within that atlas.  This helper
script converts the relevant parts into the JSON format expected by MapLibre.
No image manipulation is performed – the PNG itself is served separately.
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from s52_xml import parse_symbols


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chartsymbols", type=Path, required=True, help="Path to chartsymbols.xml")
    parser.add_argument(
        "--output", type=Path, required=True, help="Path to write sprite JSON manifest"
    )
    parser.add_argument(
        "--include",
        nargs="*",
        help="Optional list of symbol names to include; defaults to all",
    )
    parser.add_argument("--prefix", default="", help="Optional name prefix")
    return parser.parse_args()


def main() -> None:  # pragma: no cover - CLI wrapper
    args = parse_args()
    root = ET.parse(args.chartsymbols).getroot()
    wanted = set(args.include or [])

    sprites: dict[str, dict[str, int | bool]] = {}
    for name, info in parse_symbols(root).items():
        if wanted and name not in wanted:
            continue
        if not {"x", "y", "w", "h"} <= info.keys():
            continue
        key = f"{args.prefix}{name}"
        sprites[key] = {
            "x": int(info["x"]),
            "y": int(info["y"]),
            "width": int(info["w"]),
            "height": int(info["h"]),
            "pixelRatio": 1,
            "sdf": False,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(sprites, f, indent=2, sort_keys=True)
    print(f"Wrote {len(sprites)} sprite entries to {args.output}")


if __name__ == "__main__":
    main()

