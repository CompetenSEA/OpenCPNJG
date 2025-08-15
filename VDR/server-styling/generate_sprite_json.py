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
    return parser.parse_args()


def main() -> None:  # pragma: no cover - CLI wrapper
    args = parse_args()
    tree = ET.parse(args.chartsymbols)
    root = tree.getroot()

    wanted = set(args.include or [])

    sprites: dict[str, dict[str, int | bool]] = {}
    for symbol in root.findall(".//symbols/symbol"):
        # Symbol name may be stored as an attribute or child element
        name = symbol.get("name") or symbol.get("id")
        if not name:
            name_elem = symbol.find("name")
            if name_elem is not None:
                name = name_elem.text or ""
        if not name or (wanted and name not in wanted):
            continue

        bitmap = symbol.find("bitmap")
        if bitmap is None:
            continue

        # Graphics location may be a child element or attributes on <bitmap>
        gl = bitmap.find("graphics-location")
        x = gl.get("x") if gl is not None else bitmap.get("x")
        y = gl.get("y") if gl is not None else bitmap.get("y")

        try:
            entry = {
                "x": int(x or 0),
                "y": int(y or 0),
                "width": int(bitmap.get("width", "0")),
                "height": int(bitmap.get("height", "0")),
                "pixelRatio": 1,
                "sdf": False,
            }
        except ValueError:
            continue

        sprites[name] = entry  # last definition wins

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(sprites, f, indent=2, sort_keys=True)
    print(f"Wrote {len(sprites)} sprite entries to {args.output}")


if __name__ == "__main__":
    main()

