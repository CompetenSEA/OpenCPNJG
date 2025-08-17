"""Build a compact dictionary for CM93 tiles."""
from __future__ import annotations

import json
from pathlib import Path

# Static mapping; in real pipeline this would be generated from schema
_MAPPING = {
    1: "LNDARE",
    2: "DEPARE",
    3: "DEPCNT",
    4: "COALNE",
    5: "SOUNDG",
    6: "WRECKS",
    7: "OBSTRN",
    8: "LIGHTS",
}


def build(output: Path | None = None) -> Path:
    if output is None:
        base = Path(__file__).resolve().parents[1]
        output = base / "server-styling" / "dist" / "dict.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(_MAPPING, f, separators=(",", ":"))
    return output


if __name__ == "__main__":  # pragma: no cover
    build()
