"""Build a MapLibre ``style.json`` from OpenCPN S-52 assets.

The implementation intentionally focuses on a very small subset of S‑57 objects
required for the vector‑first prototype.  Colours and ordering are derived from
``chartsymbols.xml`` which is shipped with OpenCPN.  Supports multiple palettes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

from s52_xml import parse_palette_colors, parse_lookups


def _lookup_priorities(lookups: List[Dict[str, str]]) -> Dict[str, int]:
    priorities: Dict[str, int] = {}
    for lu in lookups:
        disp = lu.get("disp_prio", "")
        m = re.search(r"(\d+)", disp)
        if m:
            priorities[lu["objl"]] = int(m.group(1))
    return priorities


def get_colour(colours: Dict[str, str], token: str, fallback: str | None = None) -> str:
    if token in colours:
        return colours[token]
    if fallback and fallback in colours:
        return colours[fallback]
    return "#ff00ff"  # magenta for missing tokens


# ---------------------------------------------------------------------------
# Layer generation
# ---------------------------------------------------------------------------


def build_layers(
    colors: Dict[str, str],
    sc: float,
    source: str,
    source_layer: str,
    priorities: Dict[str, int],
) -> List[Dict[str, object]]:
    """Construct and order Tier‑1 style layers for the chosen palette."""

    layers: List[tuple[int, Dict[str, object]]] = []

    if "DEPVS" not in colors:
        print("Warning: DEPVS missing, using DEPIT1", file=sys.stderr)

    def prio(obj: str, default: int) -> int:
        return priorities.get(obj, default)

    # LNDARE ----------------------------------------------------------------
    layers.append(
        (
            prio("LNDARE", 20),
            {
                "id": "LNDARE",
                "type": "fill",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], "LNDARE"],
                "paint": {
                    "fill-color": get_colour(colors, "LANDA"),
                    "fill-outline-color": get_colour(colors, "CHBLK"),
                },
                "metadata": {"maplibre:s52": "LNDARE-LANDA"},
            },
        )
    )

    # DEPARE ----------------------------------------------------------------
    layers.append(
        (
            prio("DEPARE", 30),
            {
                "id": "DEPARE-shallow",
                "type": "fill",
                "source": source,
                "source-layer": source_layer,
                "filter": [
                    "all",
                    ["==", ["get", "OBJL"], "DEPARE"],
                    ["<", ["coalesce", ["get", "DRVAL2"], ["get", "DRVAL1"], 99999], sc],
                ],
                "paint": {"fill-color": get_colour(colors, "DEPVS", "DEPIT1")},
                "metadata": {"maplibre:s52": "DEPARE-DEPVS"},
            },
        )
    )
    layers.append(
        (
            prio("DEPARE", 31),
            {
                "id": "DEPARE-safe",
                "type": "fill",
                "source": source,
                "source-layer": source_layer,
                "filter": [
                    "all",
                    ["==", ["get", "OBJL"], "DEPARE"],
                    [
                        ">=",
                        ["coalesce", ["get", "DRVAL1"], ["get", "DRVAL2"], -99999],
                        sc,
                    ],
                ],
                "paint": {"fill-color": get_colour(colors, "DEPDW")},
                "metadata": {"maplibre:s52": "DEPARE-DEPDW"},
            },
        )
    )

    # DEPCNT ----------------------------------------------------------------
    layers.append(
        (
            prio("DEPCNT", 40),
            {
                "id": "DEPCNT-base",
                "type": "line",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], "DEPCNT"],
                "paint": {"line-color": get_colour(colors, "DEPCN"), "line-width": 1},
                "metadata": {"maplibre:s52": "DEPCNT-DEPCN"},
            },
        )
    )
    layers.append(
        (
            prio("DEPCNT", 41),
            {
                "id": "DEPCNT-lowacc",
                "type": "line",
                "source": source,
                "source-layer": source_layer,
                "filter": [
                    "all",
                    ["==", ["get", "OBJL"], "DEPCNT"],
                    [">=", ["to-number", ["get", "QUAPOS"]], 2],
                ],
                "paint": {
                    "line-color": get_colour(colors, "DEPCN"),
                    "line-width": 1,
                    "line-dasharray": [2, 2],
                },
                "metadata": {"maplibre:s52": "DEPCNT-QUAPOS>=2"},
            },
        )
    )
    layers.append(
        (
            prio("DEPCNT", 42),
            {
                "id": "DEPCNT-safety",
                "type": "line",
                "source": source,
                "source-layer": source_layer,
                "filter": [
                    "all",
                    ["==", ["get", "OBJL"], "DEPCNT"],
                    ["==", ["to-number", ["get", "VALDCO"]], sc],
                ],
                "paint": {
                    "line-color": get_colour(colors, "DEPSC"),
                    "line-width": 2,
                },
                "metadata": {"maplibre:s52": "DEPCNT-VALDCO==sc"},
            },
        )
    )

    # COALNE ----------------------------------------------------------------
    layers.append(
        (
            prio("COALNE", 50),
            {
                "id": "COALNE",
                "type": "line",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], "COALNE"],
                "paint": {
                    "line-color": get_colour(colors, "CHBLK"),
                    "line-width": 1,
                },
                "metadata": {"maplibre:s52": "COALNE-CHBLK"},
            },
        )
    )

    # UDW hazards -----------------------------------------------------------
    layers.append(
        (
            prio("OBSTRN", 54),
            {
                "id": "udw-hazards",
                "type": "symbol",
                "source": source,
                "source-layer": source_layer,
                "filter": [
                    "in",
                    ["get", "OBJL"],
                    ["literal", ["OBSTRN", "WRECKS", "UWTROC", "ROCKS"]],
                ],
                "layout": {
                    "icon-image": [
                        "case",
                        ["has", "hazardIcon"],
                        ["concat", "{SPRITE_PREFIX}", ["get", "hazardIcon"]],
                        "",
                    ],
                    "icon-allow-overlap": True,
                    "icon-anchor": "center",
                    "icon-offset": [
                        "array",
                        "number",
                        2,
                        [
                            "to-number",
                            ["coalesce", ["get", "hazardOffX"], 0],
                        ],
                        [
                            "to-number",
                            ["coalesce", ["get", "hazardOffY"], 0],
                        ],
                    ],
                    "icon-size": 1.0,
                },
                "metadata": {"maplibre:s52": "UDWHAZ-hazardIcon"},
            },
        )
    )

    # SOUNDG ----------------------------------------------------------------
    layers.append(
        (
            prio("SOUNDG", 55),
            {
                "id": "SOUNDG",
                "type": "symbol",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], "SOUNDG"],
                "layout": {
                    "text-field": [
                        "to-string",
                        ["coalesce", ["get", "VALSOU"], ["get", "VAL"]],
                    ],
                    "text-font": ["Noto Sans Regular"],
                    "text-size": 12,
                },
                "paint": {
                    "text-color": [
                        "case",
                        [
                            "<",
                            ["to-number", ["coalesce", ["get", "VALSOU"], ["get", "VAL"]]],
                            sc,
                        ],
                        get_colour(colors, "SNDG1", "#353535"),
                        get_colour(colors, "SNDG2", "#FFFFFF"),
                    ],
                    "text-halo-color": get_colour(colors, "SNDG2", "#FFFFFF"),
                    "text-halo-width": 1,
                },
                "metadata": {"maplibre:s52": "SOUNDG"},
            },
        )
    )

    layers.sort(key=lambda tup: tup[0])
    return [layer for _, layer in layers]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--chartsymbols", type=Path, required=True, help="Path to chartsymbols.xml")
    p.add_argument("--tiles-url", required=True)
    p.add_argument("--source-name", required=True)
    p.add_argument("--source-layer", required=True)
    p.add_argument("--sprite-base", required=True, help="Sprite base URL")
    p.add_argument("--glyphs", required=True, help="Glyphs URL template")
    p.add_argument("--safety-contour", type=float, default=0.0)
    p.add_argument("--sprite-prefix", default="", help="Prefix for sprite names")
    p.add_argument(
        "--palette",
        choices=["day", "dusk", "night"],
        default="day",
        help="Colour palette to use",
    )
    p.add_argument("--output", type=Path, required=True)
    return p.parse_args()


def _fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def main() -> None:  # pragma: no cover - CLI wrapper
    args = parse_args()
    root = ET.parse(args.chartsymbols).getroot()
    palette_map = {"day": "DAY_BRIGHT", "dusk": "DUSK", "night": "NIGHT"}
    colors = parse_palette_colors(root, palette_map[args.palette])
    lookups = parse_lookups(root)
    priorities = _lookup_priorities(lookups)

    layers = build_layers(
        colors, args.safety_contour, args.source_name, args.source_layer, priorities
    )

    style = {
        "version": 8,
        "name": f"OpenCPN S-52 {args.palette.capitalize()}",
        "sprite": args.sprite_base,
        "glyphs": args.glyphs,
        "sources": {
            args.source_name: {"type": "vector", "tiles": [args.tiles_url]}
        },
        "layers": layers,
    }

    # Basic validation ------------------------------------------------------
    if style.get("version") != 8:
        _fail("style.json must be version 8")
    if args.source_name not in style["sources"]:
        _fail("Vector source missing from style")
    for lyr in style["layers"]:
        if "paint" not in lyr and "layout" not in lyr:
            _fail(f"Layer {lyr['id']} missing paint/layout")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    style_json = json.dumps(style, indent=2, sort_keys=True)
    style_json = style_json.replace("{SPRITE_PREFIX}", args.sprite_prefix)
    args.output.write_text(style_json)
    print(f"Wrote style with {len(layers)} layers to {args.output}")


if __name__ == "__main__":
    main()

