from __future__ import annotations

import argparse
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Set

from s52_xml import (
    parse_day_colors,
    parse_symbols,
    parse_linestyles,
    parse_patterns,
    parse_lookups,
)


def parse_s57_catalogue(path: Path) -> Dict[str, Set[str]]:
    catalogue: Dict[str, Set[str]] = {}
    if not path or not path.exists():
        return catalogue
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            objl = row.get("Acronym") or row.get("acronym")
            if not objl:
                continue
            catalogue[objl] = set((row.get("Primitives") or row.get("primitives") or "P").split(";"))
    return catalogue


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Report S-52 XML coverage")
    p.add_argument("--chartsymbols", type=Path, required=True)
    p.add_argument("--baseline", type=Path)
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
    base = Path(__file__).resolve().parent
    dist_dir = base / "dist"
    coverage_dir = dist_dir / "coverage"
    current_path = coverage_dir / "style_coverage.json"
    prev_path = coverage_dir / "style_coverage.prev.json"
    tokens: list[str] = []
    layers: list[dict[str, str]] = []
    fallback_objs: set[str] = set()
    symbols_seen: set[str] = set()
    style_by_type: Dict[str, Set[str]] = {"symbol": set(), "line": set(), "fill": set()}
    for style_path in dist_dir.glob("style.s52.*.json"):
        style = json.loads(style_path.read_text())
        for lyr in style.get("layers", []):
            token = lyr.get("metadata", {}).get("maplibre:s52")
            if token:
                tokens.append(token)
                layers.append({"id": lyr.get("id", ""), "token": token})
                fb = lyr.get("metadata", {}).get("maplibre:s52Fallback")
                if fb:
                    fallback_objs.add(token.split("-", 1)[0])
                elif not token.endswith("-stub"):
                    lt = lyr.get("type", "")
                    style_by_type.setdefault(lt, set()).add(token.split("-", 1)[0])
            icon = lyr.get("layout", {}).get("icon-image")
            if isinstance(icon, str):
                symbols_seen.add(icon)

    lookup_objs = {l["objl"] for l in lookups}
    lookup_by_type: Dict[str, Set[str]] = {"symbol": set(), "line": set(), "fill": set()}
    for lu in lookups:
        geom = (lu.get("type", "") or "").lower()
        if geom == "point":
            lookup_by_type["symbol"].add(lu["objl"])
        elif geom == "line":
            lookup_by_type["line"].add(lu["objl"])
        else:
            lookup_by_type["fill"].add(lu["objl"])
    style_objs = {t.split("-", 1)[0] for t in tokens}
    covered = sorted(lookup_objs & style_objs)
    missing = sorted(lookup_objs - style_objs)

    baseline: dict | None = None
    if args.baseline and args.baseline.exists():
        baseline = json.loads(args.baseline.read_text())
    elif current_path.exists():
        baseline = json.loads(current_path.read_text())
    if baseline:
        prev_path.parent.mkdir(parents=True, exist_ok=True)
        prev_path.write_text(json.dumps(baseline, indent=2, sort_keys=True))

    coverage_dir.mkdir(parents=True, exist_ok=True)
    (coverage_dir / "symbols_seen.txt").write_text("\n".join(sorted(symbols_seen)))
    presence = len(covered) / len(lookup_objs) if lookup_objs else 0.0
    data = {
        "totalLookups": len(lookup_objs),
        "coveredByStyle": len(covered),
        "missingObjL": missing,
        "layers": layers,
        "presence": presence,
    }
    current_path.write_text(json.dumps(data, indent=2, sort_keys=True))

    portrayal_path = coverage_dir / "portrayal_coverage.json"
    portrayed = len(lookup_objs - fallback_objs)
    by_type: Dict[str, float] = {}
    for key, geom in [("Point", "symbol"), ("Line", "line"), ("Area", "fill")]:
        lk = lookup_by_type.get(geom, set())
        st = style_by_type.get(geom, set()) - fallback_objs
        by_type[key] = (len(st) / len(lk)) if lk else 0.0
    portrayal = {
        "coverage": (portrayed / len(lookup_objs)) if lookup_objs else 0.0,
        "portrayalMissing": sorted(fallback_objs),
        "sample": sorted(fallback_objs)[:25],
        "byType": by_type,
    }
    portrayal_path.write_text(json.dumps(portrayal, indent=2, sort_keys=True))

    print("Style coverage:")
    print(f"  total lookups: {len(lookup_objs)}")
    print(f"  covered by style: {len(covered)}")
    print(f"  missing: {len(missing)}")
    if baseline:
        prev_missing = set(baseline.get("missingObjL", []))
        newly = sorted(prev_missing - set(missing))
        print(f"  delta covered: +{len(newly)}")
        if newly:
            print("  newly covered: " + ", ".join(newly[:20]))

    # S-57 catalogue coverage ---------------------------------------------
    s57_csv = base / "dist" / "assets" / "s52" / "s57objectclasses.csv"
    if s57_csv.exists():
        catalogue = parse_s57_catalogue(s57_csv)
        catalog_keys = set(catalogue.keys())
        ignore = {"$AREAS", "$LINES", "$TEXTS"}
        active = catalog_keys - ignore
        handled = active & style_objs
        report = {
            "totalClasses": len(catalog_keys),
            "s52Lookups": len(catalog_keys & lookup_objs),
            "handledByStyles": len(handled),
            "missingClasses": sorted(active - style_objs),
            "ignoredClasses": sorted(ignore & catalog_keys),
        }
        (coverage_dir / "s57_catalogue.json").write_text(
            json.dumps(report, indent=2, sort_keys=True)
        )


if __name__ == "__main__":
    main()
