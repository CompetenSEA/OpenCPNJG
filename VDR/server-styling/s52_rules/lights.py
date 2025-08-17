"""Light portrayal helpers and symbol lookup tables."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict

# Ensure the chart-tiler package is importable
sys.path.append(str(Path(__file__).resolve().parents[2] / "chart-tiler"))
from lights import build_light_sectors, build_light_character  # type: ignore

# Mapping of ``CATLIT`` attribute values to S-52 symbol names.
# The table intentionally covers only common categories; unknown codes fall back
# to ``LIGHTS11`` which depicts a general light.
SYMBOL_BY_CATLIT: Dict[int, str] = {
    1: "LIGHTS11",  # Directional
    2: "LIGHTS11",  # Leading
    3: "LIGHTS11",  # Stand-by / reserve
    4: "LIGHTS11",
    5: "LIGHTS11",
}

__all__ = ["build_light_sectors", "build_light_character", "SYMBOL_BY_CATLIT"]
