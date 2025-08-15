"""Build a basic S-52 day style JSON for MapLibre.

Example:
    python VDR/server-styling/build_style_json.py \
      --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt" \
      --source-name cm93 \
      --safety-contour 10 \
      --output VDR/server-styling/style.s52.day.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import textwrap

DEFAULT_TILES_URL = "/tiles/cm93/{z}/{x}/{y}?fmt=mvt"
DEFAULT_SOURCE_NAME = "cm93"
DEFAULT_SC = 5.0

FALLBACK_DAY_COLORS = {
    "LANDA": "#C2B280",
    "CHBLK": "#000000",
    "DEPDW": "#FFFFFF",
    "DEPVS": "#198EC8",
    "DEPIT1": "#A5DAFF",
    "DEPCN": "#0163AC",
    "DEPSC": "#D4D4D4",
    "SNDG1": "#353535",
    "SNDG2": "#FFFFFF",
}

RULES_DIR = Path(__file__).resolve().parent / "s52_rules"
__doc__ = textwrap.dedent(__doc__ or "")


# ---------------------------------------------------------------------------
# Color handling
# ---------------------------------------------------------------------------

def load_day_colors() -> dict[str, str]:
    """Load day colors from optional rules file with safe fallbacks."""
    path = RULES_DIR / "colors.day.json"
    file_colors: dict[str, str] = {}
    if path.exists():
        try:
            file_colors = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - extremely rare
            print(f"Warning: failed to parse {path}: {exc}", file=sys.stderr)
    else:
        print(f"Warning: {path} not found; using fallback colors", file=sys.stderr)
    colors: dict[str, str] = {}
    for token, fallback in FALLBACK_DAY_COLORS.items():
        if token in file_colors:
            colors[token] = file_colors[token]
        else:
            if file_colors:
                print(
                    f"Warning: token {token} missing in {path}; using fallback {fallback}",
                    file=sys.stderr,
                )
            colors[token] = fallback
    return colors


# ---------------------------------------------------------------------------
# Layer helpers
# ---------------------------------------------------------------------------

def fill_layer(
    id_: str,
    feature: str,
    color_hex: str,
    *,
    minzoom: int | None = None,
    maxzoom: int | None = None,
    filter_: list | None = None,
) -> dict:
    layer: dict = {
        "id": id_,
        "type": "fill",
        "source": args.source_name,
        "source-layer": feature,
        "paint": {"fill-color": color_hex},
    }
    if filter_ is not None:
        layer["filter"] = filter_
    if minzoom is not None:
        layer["minzoom"] = minzoom
    if maxzoom is not None:
        layer["maxzoom"] = maxzoom
    return layer

def line_layer(
    id_: str,
    feature: str,
    color_hex: str,
    *,
    width_zoom: list = [8, 0.3, 13, 0.8],
    filter_: list | None = None,
) -> dict:
    width_expr: list = ["interpolate", ["linear"], ["zoom"]]
    for i in range(0, len(width_zoom), 2):
        width_expr.extend([width_zoom[i], width_zoom[i + 1]])
    layer: dict = {
        "id": id_,
        "type": "line",
        "source": args.source_name,
        "source-layer": feature,
        "paint": {"line-color": color_hex, "line-width": width_expr},
    }
    if filter_ is not None:
        layer["filter"] = filter_
    return layer

def symbol_text_layer(
    id_: str,
    feature: str,
    color_hex: str,
    *,
    text_expr: list,
    size_zoom: list = [10, 9, 15, 12],
    filter_: list | None = None,
) -> dict:
    size_expr: list = ["interpolate", ["linear"], ["zoom"]]
    for i in range(0, len(size_zoom), 2):
        size_expr.extend([size_zoom[i], size_zoom[i + 1]])
    layer: dict = {
        "id": id_,
        "type": "symbol",
        "source": args.source_name,
        "source-layer": feature,
        "layout": {"text-field": text_expr, "text-size": size_expr},
        "paint": {"text-color": color_hex},
    }
    if filter_ is not None:
        layer["filter"] = filter_
    return layer


# ---------------------------------------------------------------------------
# Style builder
# ---------------------------------------------------------------------------

def build_style(args: argparse.Namespace, colors: dict[str, str]) -> dict:
    sc = args.safety_contour
    style: dict = {
        "version": 8,
        "name": "S-52 Tier-1 (Day)",
        "glyphs": "/glyphs/{fontstack}/{range}.pbf",
        "sources": {
            args.source_name: {
                "type": "vector",
                "tiles": [args.tiles_url],
                "minzoom": 0,
                "maxzoom": 15,
            }
        },
        "layers": [],
    }

    layers = style["layers"]

    # LNDARE
    l = fill_layer("LNDARE", "LNDARE", colors["LANDA"])
    l["metadata"] = {"maplibre:s52": "LNDARE-LANDA"}
    l["paint"]["fill-outline-color"] = colors["CHBLK"]
    layers.append(l)

    # DEPARE bands
    shallow_filter = [
        "<",
        ["coalesce", ["get", "DRVAL2"], ["get", "DRVAL1"], 99999],
        sc,
    ]
    l = fill_layer("DEPARE-very-shallow", "DEPARE", colors["DEPVS"], filter_=shallow_filter)
    l["metadata"] = {"maplibre:s52": "DEPARE-DEPVS"}
    layers.append(l)

    deep_filter = [
        ">=",
        ["coalesce", ["get", "DRVAL1"], ["get", "DRVAL2"], -99999],
        sc,
    ]
    l = fill_layer("DEPARE-safe", "DEPARE", colors["DEPDW"], filter_=deep_filter)
    l["metadata"] = {"maplibre:s52": "DEPARE-DEPDW"}
    layers.append(l)

    # COALNE
    l = line_layer("COALNE", "COALNE", colors["CHBLK"])
    l["metadata"] = {"maplibre:s52": "COALNE-CHBLK"}
    layers.append(l)

    # DEPCNT
    l = line_layer("DEPCNT", "DEPCNT", colors["DEPCN"])
    l["metadata"] = {"maplibre:s52": "DEPCNT-DEPCN"}
    layers.append(l)

    # DEPCNT safety overlay
    sc_filter = ["==", ["to-number", ["get", "VALDCO"]], sc]
    l = line_layer("DEPCNT-safety", "DEPCNT", colors["DEPSC"], filter_=sc_filter)
    l["metadata"] = {"maplibre:s52": "DEPCNT-DEPSC"}
    layers.append(l)

    # SOUNDG
    text_expr = ["to-string", ["coalesce", ["get", "VALSOU"], ["get", "VAL"]]]
    l = symbol_text_layer("SOUNDG", "SOUNDG", colors["SNDG1"], text_expr=text_expr)
    l["metadata"] = {"maplibre:s52": "SOUNDG-SNDG1"}
    layers.append(l)

    return style


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_style(style: dict, args: argparse.Namespace) -> None:
    errors: list[str] = []
    if style.get("version") != 8:
        errors.append("style version must be 8")
    src = style.get("sources", {}).get(args.source_name)
    if not src:
        errors.append(f"source {args.source_name} missing")
    else:
        if src.get("type") != "vector":
            errors.append("source type must be vector")
        tiles = src.get("tiles") or []
        if not tiles:
            errors.append("source tiles list empty")
    for layer in style.get("layers", []):
        if "id" not in layer:
            errors.append("layer missing id")
        if "type" not in layer:
            errors.append(f"layer {layer.get('id')} missing type")
        if layer.get("source") != args.source_name:
            errors.append(f"layer {layer.get('id')} wrong source")
        if "source-layer" not in layer:
            errors.append(f"layer {layer.get('id')} missing source-layer")
        if "paint" not in layer:
            errors.append(f"layer {layer.get('id')} missing paint")
        if layer.get("type") == "symbol" and "layout" not in layer:
            errors.append(f"layer {layer.get('id')} missing layout")
    if errors:
        for msg in errors:
            print(f"Validation error: {msg}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate S-52 Day style JSON")
    p.add_argument("--output", type=Path, help="Output file path")
    p.add_argument("--tiles-url", default=DEFAULT_TILES_URL)
    p.add_argument("--source-name", default=DEFAULT_SOURCE_NAME)
    p.add_argument("--safety-contour", type=float, default=DEFAULT_SC)
    args = p.parse_args()
    if not args.tiles_url:
        print("tiles-url cannot be empty", file=sys.stderr)
        sys.exit(2)
    if not args.source_name:
        print("source-name cannot be empty", file=sys.stderr)
        sys.exit(2)
    if args.safety_contour <= 0:
        print("safety-contour must be positive", file=sys.stderr)
        sys.exit(2)
    return args

def main() -> None:
    global args
    args = parse_args()
    colors = load_day_colors()
    style = build_style(args, colors)
    validate_style(style, args)
    text = json.dumps(style, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
