"""Adapter utilities for accessing BAUV symbol and palette assets.

This module exposes a small API expected by the vector style builder.  It
provides helpers to enumerate available BAUV SVG symbols as well as loading
colour palettes when present.  The adapter assumes that the BAUV source tree is
vendored under ``VDR/BAUV`` with SVG symbols stored beneath ``src/public/svg``.

The API is intentionally tiny; it merely returns paths and dictionaries leaving
callers free to decide how the assets are consumed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, Tuple

_BASE = Path(__file__).resolve().parents[1] / "BAUV" / "src" / "public"
_SVG_DIR = _BASE / "svg"
_PALETTE_FILE = _BASE / "palette.json"


def iter_symbols() -> Iterator[Tuple[str, Path]]:
    """Yield ``(name, path)`` pairs for all available BAUV SVG symbols."""
    for path in sorted(_SVG_DIR.glob("*.svg")):
        yield path.stem, path


def symbol_path(name: str) -> Path:
    """Return the filesystem path for ``name`` within the BAUV SVG set."""
    path = _SVG_DIR / f"{name}.svg"
    if not path.exists():
        raise KeyError(f"Unknown BAUV symbol: {name}")
    return path


def load_palette() -> Dict[str, str]:
    """Return a mapping of colour token -> ``#RRGGBB``.

    BAUV currently ships a single palette stored as ``palette.json``.  If the
    palette file is absent an empty mapping is returned.
    """
    if _PALETTE_FILE.exists():
        with _PALETTE_FILE.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    return {}


__all__ = ["iter_symbols", "symbol_path", "load_palette"]
