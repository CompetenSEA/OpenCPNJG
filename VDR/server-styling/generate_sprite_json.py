#!/usr/bin/env python3
"""Generate a MapLibre sprite manifest from ``chartsymbols.xml``.

The manifest describes the location and dimensions of each symbol within the
atlas PNG used by MapLibre.  No image manipulation is performed; the original
PNG from OpenCPN is used directly.
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tree = ET.parse(args.chartsymbols)
    root = tree.getroot()

    sprites: dict[str, dict[str, int]] = {}

    for symbol in root.findall(".//symbols/symbol"):
        name_elem = symbol.find("name")
        bitmap = symbol.find("bitmap")
        if name_elem is None or bitmap is None:
            continue
        gl = bitmap.find("graphics-location")
        if gl is None:
            continue
        try:
            name = name_elem.text or ""
            x = int(gl.get("x", "0"))
            y = int(gl.get("y", "0"))
            w = int(bitmap.get("width", "0"))
            h = int(bitmap.get("height", "0"))
        except ValueError:
            continue
        sprites[name] = {
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "pixelRatio": 1,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(sprites, f, indent=2, sort_keys=True)
    print(f"Wrote {len(sprites)} sprite entries to {args.output}")


if __name__ == "__main__":
    main()
