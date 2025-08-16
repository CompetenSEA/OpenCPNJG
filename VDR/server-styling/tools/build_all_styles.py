"""Build day, dusk and night styles and validate them."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build_style_json.py"
VALIDATE = ROOT / "tools" / "validate_style.mjs"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--chartsymbols", type=Path, required=True)
    p.add_argument("--tiles-url", required=True)
    p.add_argument("--source-name", required=True)
    p.add_argument("--source-layer", required=True)
    p.add_argument("--sprite-base", required=True)
    p.add_argument("--sprite-prefix", default="")
    p.add_argument("--glyphs", required=True)
    p.add_argument("--safety-contour", type=float, default=0.0)
    p.add_argument("--emit-name")
    p.add_argument("--auto-cover", action="store_true")
    p.add_argument("--s57-catalogue", type=Path)
    p.add_argument("--labels", action="store_true")
    return p.parse_args()


def main() -> int:  # pragma: no cover - CLI helper
    args = parse_args()
    palettes = ["day", "dusk", "night"]
    for pal in palettes:
        out = ROOT / "dist" / f"style.s52.{pal}.json"
        sprite_base = args.sprite_base.replace("day", pal)
        emit_name = args.emit_name.format(palette=pal) if args.emit_name else None
        cmd = [
            sys.executable,
            str(BUILD),
            "--chartsymbols",
            str(args.chartsymbols),
            "--tiles-url",
            args.tiles_url,
            "--source-name",
            args.source_name,
            "--source-layer",
            args.source_layer,
            "--sprite-base",
            sprite_base,
            "--glyphs",
            args.glyphs,
            "--safety-contour",
            str(args.safety_contour),
            "--sprite-prefix",
            args.sprite_prefix,
            *( ["--emit-name", emit_name] if emit_name else [] ),
            *( ["--auto-cover"] if args.auto_cover else [] ),
            *( ["--s57-catalogue", str(args.s57_catalogue)] if args.s57_catalogue else [] ),
            *( ["--labels"] if args.labels else [] ),
            "--palette",
            pal,
            "--output",
            str(out),
        ]
        subprocess.check_call(cmd)
        try:
            proc = subprocess.run(["node", str(VALIDATE), str(out)], check=False)
            if proc.returncode != 0:
                print("maplibre-gl-style-spec missing; skipping validation", file=sys.stderr)
        except FileNotFoundError:
            print("Node not installed; skipping validation", file=sys.stderr)
    print("Built styles:", ", ".join(palettes))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI helper
    raise SystemExit(main())

