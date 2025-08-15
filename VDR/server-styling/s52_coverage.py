from __future__ import annotations

import argparse
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


if __name__ == "__main__":
    main()
