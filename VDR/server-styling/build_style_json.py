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
from typing import Dict, List, Set

from s52_xml import (
    parse_palette_colors,
    parse_lookups,
    parse_symbols,
    parse_linestyles,
    parse_patterns,
    parse_s57_catalogue,
)


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


def generate_stub_layers_from_catalog(
    colors: Dict[str, str],
    catalogue: Dict[str, Set[str]],
    existing_objls: Set[str],
    source: str,
    source_layer: str,
    priorities: Dict[str, int],
) -> List[tuple[int, Dict[str, object]]]:
    layers: List[tuple[int, Dict[str, object]]] = []
    for objl, prims in catalogue.items():
        if objl in existing_objls:
            continue
        prio = priorities.get(objl, 50)
        for prim in prims:
            lyr_id = f"{objl}-{prim}"
            metadata = {"maplibre:s52": f"{objl}-stub"}
            if prim == "P":
                layer = {
                    "id": lyr_id,
                    "type": "symbol",
                    "source": source,
                    "source-layer": source_layer,
                    "filter": ["==", ["get", "OBJL"], objl],
                    "layout": {
                        "icon-image": "marker-15",
                        "icon-allow-overlap": True,
                    },
                    "metadata": metadata,
                }
            elif prim == "L":
                layer = {
                    "id": lyr_id,
                    "type": "line",
                    "source": source,
                    "source-layer": source_layer,
                    "filter": ["==", ["get", "OBJL"], objl],
                    "paint": {
                        "line-color": get_colour(colors, "CHBLK"),
                        "line-width": 1,
                    },
                    "metadata": metadata,
                }
            else:  # Area
                layer = {
                    "id": lyr_id,
                    "type": "fill",
                    "source": source,
                    "source-layer": source_layer,
                    "filter": ["==", ["get", "OBJL"], objl],
                    "paint": {
                        "fill-color": get_colour(colors, "LANDA"),
                        "fill-outline-color": get_colour(colors, "CHBLK"),
                    },
                    "metadata": metadata,
                }
            layers.append((prio, layer))
    layers.sort(key=lambda tup: tup[0])
    return layers


# ---------------------------------------------------------------------------
# Layer generation
# ---------------------------------------------------------------------------


def build_layers(
    colors: Dict[str, str],
    sc: float,
    source: str,
    source_layer: str,
    priorities: Dict[str, int],
    symbols: Dict[str, Dict[str, object]],
    linestyles: Dict[str, Dict[str, object]],
    labels: bool = False,
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
                "metadata": {"maplibre:s52": "LNDARE-AC(LANDA)"},
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
                "metadata": {"maplibre:s52": "DEPARE-AC(DEPVS)"},
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
                "metadata": {"maplibre:s52": "DEPARE-AC(DEPDW)"},
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
                "metadata": {"maplibre:s52": "DEPCNT-LS(DEPCN)"},
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
                "metadata": {"maplibre:s52": "DEPCNT-LS(DEPCN)"},
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
                "metadata": {"maplibre:s52": "DEPCNT-LS(DEPSC)"},
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
                "metadata": {"maplibre:s52": "COALNE-LS(CHBLK)"},
            },
        )
    )

    # Point seamarks -------------------------------------------------------
    seamarks = [
        "BCNLAT",
        "BCNCAR",
        "BCNISD",
        "BOYISD",
        "BOYLAT",
        "BOYCAR",
        "RTPBCN",
    ]
    for obj in seamarks:
        sym_name = None
        meta = None
        for suffix in ("01", "02", "1", ""):
            cand = obj + suffix
            if cand in symbols:
                sym_name = cand
                meta = symbols[cand]
                break
        if not sym_name:
            continue
        layout: Dict[str, object] = {
            "icon-image": [
                "concat",
                "{SPRITE_PREFIX}",
                [
                    "case",
                    ["has", "hazardIcon"],
                    ["get", "hazardIcon"],
                    sym_name,
                ],
            ],
            "icon-allow-overlap": True,
            "icon-anchor": "center",
        }
        anchor = meta.get("anchor")
        if anchor:
            ax, ay = anchor
            off_x = ax - meta.get("w", 0) / 2
            off_y = ay - meta.get("h", 0) / 2
            if off_x or off_y:
                layout["icon-offset"] = [off_x, off_y]
        if meta.get("rotate"):
            layout["icon-rotate"] = ["coalesce", ["get", "ORIENT"], 0]
        layer_def: Dict[str, object] = {
            "id": obj,
            "type": "symbol",
            "source": source,
            "source-layer": source_layer,
            "filter": ["==", ["get", "OBJL"], obj],
            "layout": layout,
            "metadata": {"maplibre:s52": f"{obj}-SY({sym_name})"},
        }
        if labels:
            layer_def.setdefault("layout", {})["text-field"] = [
                "coalesce",
                ["get", "OBJNAM"],
                "",
            ]
            layer_def["layout"]["text-font"] = ["Noto Sans Regular"]
            paint: Dict[str, object] = {
                "text-color": get_colour(colors, "CHBLK"),
                "text-halo-color": "#ffffff",
                "text-halo-width": 1,
            }
            layer_def["paint"] = paint
        layers.append((prio(obj, 52), layer_def))

    if labels:
        name_objs = ["BCNLAT", "BCNCAR", "BCNISD", "BOYISD", "BOYLAT", "BOYCAR", "RTPBCN"]
        for obj in name_objs:
            layers.append(
                (
                    prio(obj, 53),
                    {
                        "id": f"{obj}-name",
                        "type": "symbol",
                        "source": source,
                        "source-layer": source_layer,
                        "minzoom": 11,
                        "filter": ["==", ["get", "OBJL"], obj],
                        "layout": {
                            "text-field": [
                                "coalesce",
                                ["get", "OBJNAM"],
                                ["get", "NOBJNM"],
                                "",
                            ],
                            "text-font": ["Noto Sans Regular"],
                            "text-size": [
                                "interpolate",
                                ["linear"],
                                ["zoom"],
                                10,
                                10,
                                14,
                                12,
                                17,
                                14,
                            ],
                            "text-allow-overlap": False,
                            "symbol-sort-key": [
                                "coalesce",
                                ["get", "scamin"],
                                ["get", "rank"],
                                0,
                            ],
                        },
                        "paint": {
                            "text-color": get_colour(colors, "CHBLK"),
                            "text-halo-color": "#ffffff",
                            "text-halo-width": 1,
                        },
                        "metadata": {"maplibre:s52": "NAVAID-SY(nameLabel)"},
                    },
                )
            )

    layers.append(
        (
            prio("LIGHTS", 52),
            {
                "id": "LIGHTS-sector",
                "type": "line",
                "source": source,
                "source-layer": source_layer,
                "filter": [
                    "all",
                    ["==", ["get", "OBJL"], "LIGHTS"],
                    ["has", "SECTR1"],
                    ["has", "SECTR2"],
                ],
                "paint": {
                    "line-color": get_colour(colors, "CHBLK"),
                    "line-width": 1,
                    "line-dasharray": [2, 2],
                },
                "metadata": {"maplibre:s52": "LIGHTS-LS(sector)"},
            },
        )
    )

    # Caution lines --------------------------------------------------------
    dash_map = {
        "solid": None,
        "dash": [4, 2],
        "dot": [1, 2],
        "dashdot": [4, 2, 1, 2],
    }
    for obj in ["CBLARE", "PIPARE"]:
        ls_meta = None
        for cand in (obj, obj + "01", obj + "1"):
            if cand in linestyles:
                ls_meta = linestyles[cand]
                break
        if not ls_meta:
            continue
        paint: Dict[str, object] = {
            "line-color": get_colour(colors, ls_meta.get("color-token", ""), "CHBLK"),
            "line-width": ls_meta.get("width", 1),
        }
        dash = dash_map.get(ls_meta.get("pattern", "solid"))
        if dash:
            paint["line-dasharray"] = dash
        layers.append(
            (
                prio(obj, 53),
                {
                    "id": obj,
                    "type": "line",
                    "source": source,
                    "source-layer": source_layer,
                    "filter": ["==", ["get", "OBJL"], obj],
                    "paint": paint,
                    "metadata": {"maplibre:s52": f"{obj}-LS({ls_meta.get('color-token', '')})"},
                },
            )
        )

    # Area stubs ----------------------------------------------------------
    layers.append(
        (
            prio("SEAARE", 10),
            {
                "id": "SEAARE",
                "type": "fill",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], "SEAARE"],
                "paint": {
                    "fill-color": get_colour(colors, "DEPDW"),
                    "fill-outline-color": get_colour(colors, "CHBLK"),
                },
                "metadata": {"maplibre:s52": "SEAARE-AC(DEPDW)"},
            },
        )
    )
    for obj in ["ACHARE", "ADMARE"]:
        layers.append(
            (
                prio(obj, 11),
                {
                    "id": f"{obj}-outline",
                    "type": "line",
                    "source": source,
                    "source-layer": source_layer,
                    "filter": ["==", ["get", "OBJL"], obj],
                    "paint": {
                        "line-color": get_colour(colors, "CHBLK"),
                        "line-width": 1,
                    },
                    "metadata": {"maplibre:s52": f"{obj}-LS(CHBLK)"},
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
                        "concat",
                        "{SPRITE_PREFIX}",
                        [
                            "case",
                            ["has", "hazardIcon"],
                            [
                                "case",
                                ["==", ["get", "WATLEV"], 2],
                                ["concat", ["get", "hazardIcon"], "-int"],
                                ["get", "hazardIcon"],
                            ],
                            [
                                "case",
                                ["==", ["get", "OBJL"], "WRECKS"],
                                "DANGER51",
                                ["==", ["get", "OBJL"], "ROCKS"],
                                "DANGER01",
                                ["==", ["get", "OBJL"], "UWTROC"],
                                "DANGER31",
                                ["==", ["get", "OBJL"], "OBSTRN"],
                                "DANGER21",
                                "DANGER51",
                            ],
                        ],
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
                "metadata": {"maplibre:s52": "UDWHAZ-SY(hazardIcon)"},
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
                        "number-format",
                        [
                            "to-number",
                            ["coalesce", ["get", "VALSOU"], ["get", "VAL"]],
                        ],
                        {"minFractionDigits": 0, "maxFractionDigits": 1},
                    ],
                    "text-font": ["Noto Sans Regular"],
                    "text-size": [
                        "interpolate",
                        ["linear"],
                        ["zoom"],
                        10,
                        9,
                        13,
                        11,
                        16,
                        13,
                    ],
                },
                "minzoom": 10,
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
                "metadata": {"maplibre:s52": "SOUNDG-SY(text)"},
            },
        )
    )

    if labels:
        layers.append(
            (
                prio("OBJNAM", 90),
                {
                    "id": "feature-names",
                    "type": "symbol",
                    "source": source,
                    "source-layer": source_layer,
                    "filter": ["any", ["has", "OBJNAM"], ["has", "NOBJNM"]],
                    "layout": {
                        "text-field": [
                            "coalesce",
                            ["get", "OBJNAM"],
                            ["get", "NOBJNM"],
                        ],
                        "text-font": ["Noto Sans Regular"],
                        "text-size": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            5,
                            12,
                            12,
                            16,
                        ],
                    },
                    "paint": {
                        "text-color": get_colour(colors, "CHBLK"),
                        "text-halo-color": "#ffffff",
                        "text-halo-width": 1,
                    },
                    "metadata": {"maplibre:s52": "OBJNAM-label"},
                },
            )
        )

    layers.sort(key=lambda tup: tup[0])
    return [layer for _, layer in layers]


def _norm_dash(pattern: str | None) -> List[float] | None:
    dash_map = {
        "solid": None,
        "dash": [4, 2],
        "dot": [1, 2],
        "dashdot": [4, 2, 1, 2],
    }
    return dash_map.get(pattern or "solid")


def _light_label_expr() -> List[object]:
    """Compose a basic light label expression from common attributes."""
    return [
        "concat",
        ["coalesce", ["get", "LITCHR"], ""],
        [
            "case",
            ["any", ["has", "COLOUR"], ["has", "COLOUR2"], ["has", "COLPAT"]],
            [
                "concat",
                " ",
                [
                    "coalesce",
                    ["get", "COLOUR"],
                    ["get", "COLOUR2"],
                    ["get", "COLPAT"],
                    "",
                ],
            ],
            "",
        ],
        [
            "case",
            ["has", "HEIGHT"],
            ["concat", " ", ["to-string", ["get", "HEIGHT"]], "m"],
            "",
        ],
        [
            "case",
            ["has", "RANGE"],
            ["concat", " ", ["to-string", ["get", "RANGE"]], "M"],
            "",
        ],
    ]


def generate_layers_from_lookups(
    colors: Dict[str, str],
    lookups: List[Dict[str, object]],
    symbols: Dict[str, Dict[str, object]],
    linestyles: Dict[str, Dict[str, object]],
    patterns: Dict[str, Dict[str, object]],
    source: str,
    source_layer: str,
    priorities: Dict[str, int],
    labels: bool = False,
) -> List[tuple[int, Dict[str, object]]]:
    """Synthesise minimal layers for all lookups."""

    layers: List[tuple[int, Dict[str, object]]] = []
    for lu in lookups:
        objl = lu.get("objl", "")
        instr = lu.get("instruction", "") or ""
        geom = (lu.get("type", "") or "").lower()
        prio = priorities.get(objl, 50)
        metadata: Dict[str, object] = {"maplibre:s52": f"{objl}"}
        fallback: str | None = None

        if geom == "point":
            sym_match = re.search(r"SY\(([A-Z0-9]+)\)", instr)
            sym = sym_match.group(1) if sym_match else None
            layout: Dict[str, object] = {"icon-allow-overlap": True}
            if sym and sym in symbols:
                meta = symbols[sym]
                layout["icon-image"] = ["concat", "{SPRITE_PREFIX}", sym]
                layout["icon-anchor"] = "center"
                anchor = meta.get("anchor")
                if anchor:
                    ax, ay = anchor
                    off_x = ax - meta.get("w", 0) / 2
                    off_y = ay - meta.get("h", 0) / 2
                    if off_x or off_y:
                        layout["icon-offset"] = [off_x, off_y]
                if meta.get("rotate"):
                    layout["icon-rotate"] = ["coalesce", ["get", "ORIENT"], 0]
                metadata["maplibre:s52"] = f"{objl}-SY({sym})"
            else:
                layout["icon-image"] = "marker-15"
                fallback = "missingSymbol"
                metadata["maplibre:s52"] = f"{objl}-stub"
            layer = {
                "id": objl,
                "type": "symbol",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], objl],
                "layout": layout,
                "metadata": metadata,
            }
            if labels and objl == "LIGHTS":
                layer.setdefault("layout", {})
                layer["layout"]["text-field"] = _light_label_expr()
                layer["layout"]["text-font"] = ["Noto Sans Regular"]
                layer.setdefault("paint", {})
                layer["paint"]["text-color"] = get_colour(colors, "CHBLK")
                layer["paint"]["text-halo-color"] = "#ffffff"
                layer["paint"]["text-halo-width"] = 1
        elif geom == "line":
            ls_match = re.search(r"LS\(([^,]+),([^,]+),([^\)]+)\)", instr)
            color_token = None
            width = 1.0
            pattern_name = None
            if ls_match:
                pattern_name, width_s, color_token = [p.strip() for p in ls_match.groups()]
                try:
                    width = float(width_s)
                except ValueError:
                    width = 1.0
            ls_meta = linestyles.get(pattern_name or "")
            paint: Dict[str, object] = {}
            if ls_meta:
                color_token = ls_meta.get("color-token") or color_token
                width = ls_meta.get("width", width)
                dash = _norm_dash(ls_meta.get("pattern"))
                if dash:
                    paint["line-dasharray"] = dash
                metadata["maplibre:s52"] = f"{objl}-LS({color_token or pattern_name or ''})"
            else:
                if pattern_name:
                    fallback = "missingLineStyle"
                metadata["maplibre:s52"] = f"{objl}-stub"
            paint["line-color"] = get_colour(colors, color_token or "CHBLK")
            paint["line-width"] = width
            layer = {
                "id": objl,
                "type": "line",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], objl],
                "paint": paint,
                "metadata": metadata,
            }
        else:  # area or unknown
            col_match = re.search(r"AC\(([A-Z0-9]+)\)", instr)
            color_token = col_match.group(1) if col_match else None
            pat_match = re.search(r"AP\(([A-Z0-9]+)\)", instr)
            pat = pat_match.group(1) if pat_match else None
            paint: Dict[str, object] = {}
            if pat and pat in patterns and patterns[pat].get("type") == "bitmap":
                paint["fill-pattern"] = ["concat", "{SPRITE_PREFIX}", pat]
                metadata["maplibre:s52"] = f"{objl}-AP({pat})"
            elif color_token:
                paint["fill-color"] = get_colour(colors, color_token)
                metadata["maplibre:s52"] = f"{objl}-AC({color_token})"
            else:
                if pat:
                    fallback = "missingPattern"
                else:
                    fallback = "missingColor"
                paint["fill-color"] = get_colour(colors, "LANDA")
                metadata["maplibre:s52"] = f"{objl}-stub"
            paint["fill-outline-color"] = get_colour(colors, "CHBLK")
            layer = {
                "id": objl,
                "type": "fill",
                "source": source,
                "source-layer": source_layer,
                "filter": ["==", ["get", "OBJL"], objl],
                "paint": paint,
                "metadata": metadata,
            }

        if fallback:
            metadata["maplibre:s52Fallback"] = fallback
        layers.append((prio, layer))

    layers.sort(key=lambda tup: tup[0])
    return layers


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
    p.add_argument("--emit-name", help="Override style.name in output")
    p.add_argument("--auto-cover", action="store_true", help="Generate layers for all lookups")
    p.add_argument("--s57-catalogue", type=Path)
    p.add_argument("--labels", action="store_true", help="Render labels for certain features")
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
    if not args.chartsymbols.exists():
        _fail(
            "chartsymbols.xml missing. Run 'python VDR/server-styling/"
            "sync_opencpn_assets.py --lock VDR/server-styling/opencpn-assets.lock "
            "--dest VDR/server-styling/dist/assets/s52 --force'"
        )
    root = ET.parse(args.chartsymbols).getroot()
    palette_map = {"day": "DAY_BRIGHT", "dusk": "DUSK", "night": "NIGHT"}
    colors = parse_palette_colors(root, palette_map[args.palette])
    lookups = parse_lookups(root)
    priorities = _lookup_priorities(lookups)
    symbols = parse_symbols(root)
    linestyles = parse_linestyles(root)
    patterns = parse_patterns(root)

    layers = build_layers(
        colors,
        args.safety_contour,
        args.source_name,
        args.source_layer,
        priorities,
        symbols,
        linestyles,
        labels=args.labels,
    )

    if args.auto_cover:
        auto_layers = generate_layers_from_lookups(
            colors,
            lookups,
            symbols,
            linestyles,
            patterns,
            args.source_name,
            args.source_layer,
            priorities,
            labels=args.labels,
        )
        existing_ids = {lyr["id"] for lyr in layers}
        for _, lyr in auto_layers:
            if lyr["id"] not in existing_ids:
                layers.append(lyr)
                existing_ids.add(lyr["id"])
        cat_path = args.s57_catalogue
        if not cat_path:
            default_cat = Path(__file__).resolve().parent / "dist" / "assets" / "s52" / "s57objectclasses.csv"
            if default_cat.exists():
                cat_path = default_cat
        if cat_path and cat_path.exists():
            catalogue = parse_s57_catalogue(cat_path)
            for ign in ["$AREAS", "$LINES", "$TEXTS"]:
                catalogue.pop(ign, None)
            stub_layers = generate_stub_layers_from_catalog(
                colors,
                catalogue,
                {lu["objl"] for lu in lookups},
                args.source_name,
                args.source_layer,
                priorities,
            )
            for _, lyr in stub_layers:
                if lyr["id"] not in existing_ids:
                    layers.append(lyr)
                    existing_ids.add(lyr["id"])

    style = {
        "version": 8,
        "name": args.emit_name
        or f"OpenCPN S-52 {args.palette.capitalize()}",
        "sprite": args.sprite_base,
        "glyphs": args.glyphs,
        "sources": {
            args.source_name: {"type": "vector", "tiles": [args.tiles_url]}
        },
        "layers": layers,
        "metadata": {"maplibre:s52.palette": args.palette},
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
