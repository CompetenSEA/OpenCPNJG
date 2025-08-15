#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate a MapLibre style.json for S-52 chart rendering.

This script loads color tables and rendering rules from the OpenCPN S-52 C++
library (exposed to Python as :mod:`ps52`) and converts them to a MapLibre
``style.json``.  It is intended as a small bootstrap tool for creating vector
tile styles without hand‑authoring hundreds of S-52 rules.

Example
-------
    python VDR/server-styling/build_style_json.py \
        --rulebook VDR/server-styling/s52_rules \
        --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt" \
        --source-name cm93 \
        --output VDR/server-styling/style.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Optional ps52 bindings
# ---------------------------------------------------------------------------

# The real environment provides a compiled ``ps52`` Python module built using
# pybind11.  For development environments where this shared object is missing we
# fall back to a very small mock that exposes the same API surface.  This keeps
# the script runnable in CI and for documentation examples.
try:  # pragma: no cover - exercised only when ps52 is available
    import ps52  # type: ignore
except Exception:  # pragma: no cover - mock path
    print(
        "WARNING: Using mock 'ps52' library. Output will be based on dummy data.",
        file=sys.stderr,
    )

    class MockColor:
        def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
            self.r, self.g, self.b, self.a = r, g, b, a

    class MockFillRule:
        def __init__(self, objl: str, color_token: str) -> None:
            self.objl = objl
            self.colorToken = color_token

    class MockLineRule:
        def __init__(self, objl: str, pattern: str, width: float, color_token: str) -> None:
            self.objl = objl
            self.pattern = pattern
            self.width = width
            self.colorToken = color_token

    class MockSymbolRule:
        def __init__(self, objl: str, icon_name: str, size: float) -> None:
            self.objl = objl
            self.iconName = icon_name
            self.size = size

    class MockCategoryRuleSet:
        def __init__(self) -> None:
            self.fillRules = [
                MockFillRule("LNDARE", "LANDA"),
                MockFillRule("DEPARE", "DEPIT1"),
            ]
            self.lineRules = [
                MockLineRule("COALNE", "solid", 1.5, "CHBLK"),
                MockLineRule("DEPCNT", "dash", 1.0, "CHBLK"),
            ]
            self.symbolRules = [MockSymbolRule("SOUNDG", "SOUNDG", 10.0)]

    class MockRuleBook:
        def GetCategoryList(self) -> List[str]:
            return ["DEPARE", "LNDARE", "COALNE", "DEPCNT", "SOUNDG"]

        def GetRules(self, category: str) -> MockCategoryRuleSet:  # noqa: ARG002
            return MockCategoryRuleSet()

        @staticmethod
        def Load(path: str) -> "MockRuleBook":  # noqa: D401
            print(f"MOCK: Loading RuleBook from {path}")
            return MockRuleBook()

    class MockColorTable:
        def GetColorTokens(self) -> Dict[str, MockColor]:
            return {
                "LANDA": MockColor(204, 204, 0),
                "DEPIT1": MockColor(160, 160, 240),
                "CHBLK": MockColor(0, 0, 0),
            }

        @staticmethod
        def Load(path: str) -> "MockColorTable":  # noqa: D401
            print(f"MOCK: Loading ColorTable from {path}")
            return MockColorTable()

    class MockPs52:  # pragma: no cover - executed only with missing ps52
        RuleBook = MockRuleBook
        ColorTable = MockColorTable
        Color = MockColor

    ps52 = MockPs52()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the script."""

    parser = argparse.ArgumentParser(
        description="Generate a MapLibre style.json from OpenCPN S-52 rules."
    )
    parser.add_argument(
        "--rulebook",
        required=True,
        type=Path,
        help="Absolute path to the root of the S-52 Rules directory",
    )
    parser.add_argument(
        "--output",
        default=Path("./dist/style.json"),
        type=Path,
        help="Path to write the final style.json file",
    )
    parser.add_argument(
        "--tiles-url",
        default="/tiles/cm93/{z}/{x}/{y}?fmt=mvt",
        help="Template URL for vector tiles",
    )
    parser.add_argument(
        "--source-name",
        default="cm93",
        help="Name of the vector tile source used in the style",
    )
    parser.add_argument(
        "--source-layer",
        default="features",
        help="Name of the source layer containing S-57 features",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        default=["LNDARE", "DEPARE", "COALNE", "DEPCNT"],
        help="Limit output to these S-57 object categories",
    )
    parser.add_argument(
        "--palette",
        default="day",
        choices=["day", "dusk", "night"],
        help="Color palette to use from the rulebook",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def color_to_hex(color: ps52.Color) -> str:
    """Convert a :class:`ps52.Color` to an ``#RRGGBB`` string."""

    return f"#{color.r:02x}{color.g:02x}{color.b:02x}"


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def main() -> None:  # pragma: no cover - CLI wrapper
    args = parse_args()
    palette_name = args.palette

    print(f"Loading S-52 rulebook from: {args.rulebook}")
    print(f"Using '{palette_name}' color palette.")

    try:
        # 1. Load color tokens from the C++ library
        color_table = ps52.ColorTable.Load(str(args.rulebook))
        color_tokens_cpp = color_table.GetColorTokens()

        color_map = {
            token: color_to_hex(color) for token, color in color_tokens_cpp.items()
        }
        print(f"Successfully loaded {len(color_map)} color tokens.")

        # 2. Load the S-52 rulebook
        rulebook = ps52.RuleBook.Load(str(args.rulebook))
        all_categories = set(rulebook.GetCategoryList())
        categories = [c for c in args.categories if c in all_categories]
        categories_set = set(categories)
        print(f"Found {len(categories)} S-57 object categories in rulebook.")

        # 3. Translate rules into MapLibre layers
        maplibre_layers: List[Dict[str, object]] = []
        processed: set[str] = set()
        for category in categories:
            rule_set = rulebook.GetRules(category)

            # Fill rules
            for rule in getattr(rule_set, "fillRules", []):
                if rule.objl not in categories_set or rule.objl in processed:
                    continue
                layer = {
                    "id": f"{rule.objl}-fill",
                    "type": "fill",
                    "source": args.source_name,
                    "source-layer": args.source_layer,
                    "filter": ["==", "OBJL", rule.objl],
                    "paint": {
                        "fill-color": color_map.get(rule.colorToken, "#FF00FF")
                    },
                }
                maplibre_layers.append(layer)
                processed.add(rule.objl)

            # Line rules
            for rule in getattr(rule_set, "lineRules", []):
                if rule.objl not in categories_set or rule.objl in processed:
                    continue
                layer = {
                    "id": f"{rule.objl}-line",
                    "type": "line",
                    "source": args.source_name,
                    "source-layer": args.source_layer,
                    "filter": ["==", "OBJL", rule.objl],
                    "paint": {
                        "line-color": color_map.get(rule.colorToken, "#FF00FF"),
                        "line-width": rule.width,
                    },
                }
                maplibre_layers.append(layer)
                processed.add(rule.objl)

            # Symbol rules
            for rule in getattr(rule_set, "symbolRules", []):
                if rule.objl not in categories_set or rule.objl in processed:
                    continue
                layer = {
                    "id": f"{rule.objl}-icon",
                    "type": "symbol",
                    "source": args.source_name,
                    "source-layer": args.source_layer,
                    "filter": ["==", "OBJL", rule.objl],
                    "layout": {
                        "icon-image": getattr(rule, "iconName", ""),
                        "icon-size": getattr(rule, "size", 20.0) / 20.0,
                        "icon-allow-overlap": True,
                    },
                }
                maplibre_layers.append(layer)
                processed.add(rule.objl)

        print(f"Generated {len(maplibre_layers)} MapLibre layers.")

        # 4. Assemble the final style.json
        style_json: Dict[str, object] = {
            "version": 8,
            "name": f"OpenCPN S-52 Style - {palette_name.capitalize()}",
            "sources": {
                args.source_name: {
                    "type": "vector",
                    "tiles": [args.tiles_url],
                }
            },
            "layers": maplibre_layers,
        }

        # 5. Write the output file
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as f:
            json.dump(style_json, f, indent=2)

        print(f"Successfully wrote style.json to: {args.output}")

    except Exception as exc:  # pragma: no cover - runtime errors
        print(f"An error occurred: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
