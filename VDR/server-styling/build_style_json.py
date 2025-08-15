"""Generate a basic S-52 style for MapLibre."""
from __future__ import annotations

import json
from pathlib import Path

RULES_DIR = Path(__file__).parent / "s52_rules"


def build_style() -> dict:
    colors = json.loads((RULES_DIR / "colors.json").read_text())
    layers_cfg = json.loads((RULES_DIR / "layers.json").read_text())
    expressions = json.loads((RULES_DIR / "expressions.json").read_text())
    layers = []
    for layer in layers_cfg:
        color = colors[layer["color"]]
        if layer["type"] == "fill":
            paint = {"fill-color": color}
        elif layer["type"] == "line":
            paint = {"line-color": color}
        else:  # symbol
            paint = {"text-color": color}
        expr = expressions.get(layer["feature"])
        if expr:
            key = next(iter(paint))
            paint[key] = expr
        layers.append(
            {
                "id": layer["feature"],
                "type": layer["type"],
                "source": "cm93",
                "paint": paint,
            }
        )
    return {"version": 8, "sources": {"cm93": {"type": "vector"}}, "layers": layers}


def main(output: Path | None = None) -> None:
    style = build_style()
    text = json.dumps(style, indent=2)
    if output:
        output.write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Build MapLibre style JSON")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    main(args.output)
