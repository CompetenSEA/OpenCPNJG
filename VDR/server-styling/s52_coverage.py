from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from s52_xml import (
    parse_day_colors,
    parse_symbols,
    parse_linestyles,
    parse_patterns,
    parse_lookups,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Report S-52 XML coverage")
    p.add_argument("--chartsymbols", type=Path, required=True)
    return p.parse_args()


def main() -> None:  # pragma: no cover - CLI helper
    args = parse_args()
    root = ET.parse(args.chartsymbols).getroot()
    colors = parse_day_colors(root)
    symbols = parse_symbols(root)
    linestyles = parse_linestyles(root)
    patterns = parse_patterns(root)
    lookups = parse_lookups(root)

    print(f"Colors: {len(colors)}")
    print(f"Symbols: {len(symbols)}")
    print(f"Line styles: {len(linestyles)}")
    print(f"Patterns: {len(patterns)}")
    print(f"Lookups: {len(lookups)}")
    for name in ["ISODGR51", "DANGER51", "WRECKS01"]:
        print(f"Symbol {name}: {'yes' if name in symbols else 'no'}")

    # Style coverage -------------------------------------------------------
    style_path = Path(__file__).resolve().parent / "dist" / "style.s52.day.json"
    coverage_dir = Path(__file__).resolve().parent / "dist" / "coverage"
    tokens: list[str] = []
    layers: list[dict[str, str]] = []
    symbols_seen: set[str] = set()
    if style_path.exists():
        style = json.loads(style_path.read_text())
        for lyr in style.get("layers", []):
            token = lyr.get("metadata", {}).get("maplibre:s52")
            if token:
                tokens.append(token)
                layers.append({"id": lyr.get("id", ""), "token": token})
            icon = lyr.get("layout", {}).get("icon-image")
            if isinstance(icon, str):
                symbols_seen.add(icon)

    lookup_objs = {l["objl"] for l in lookups}
    style_objs = {t.split("-", 1)[0] for t in tokens}
    covered = sorted(lookup_objs & style_objs)
    missing = sorted(lookup_objs - style_objs)

    coverage_dir.mkdir(parents=True, exist_ok=True)
    (coverage_dir / "symbols_seen.txt").write_text("\n".join(sorted(symbols_seen)))
    (coverage_dir / "style_coverage.json").write_text(
        json.dumps(
            {
                "totalLookups": len(lookup_objs),
                "coveredByStyle": len(covered),
                "missingObjL": missing,
                "layers": layers,
            },
            indent=2,
            sort_keys=True,
        )
    )

    print("Style coverage:")
    print(f"  total lookups: {len(lookup_objs)}")
    print(f"  covered by style: {len(covered)}")
    print(f"  missing: {len(missing)}")


if __name__ == "__main__":
    main()
