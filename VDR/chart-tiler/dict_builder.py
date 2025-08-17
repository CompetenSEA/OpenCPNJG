"""Build a compact dictionary for CM93 tiles.

The previous implementation emitted a static mapping of integer codes to
object class names.  To support labels and light descriptions we now read
definitions from a schema file and optionally merge light character codes
from a database table.  The resulting JSON structure has two top‑level keys:

``objects``
    Mapping of object class IDs to dictionaries with ``name`` and optional
    ``label`` attribute lists.

``lights``
    Mapping of CRC32 codes (as strings) to human readable light character
    descriptions.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any

import yaml


def _load_schema(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build(
    output: Path | None = None,
    schema: Path | None = None,
    db_path: Path | None = None,
) -> Path:
    """Create ``dict.json`` from the provided sources."""

    root = Path(__file__).resolve().parents[1]
    base = Path(__file__).resolve().parent
    if output is None:
        output = root / "server-styling" / "dist" / "dict.json"
    if schema is None:
        schema = base / "config" / "cm93_dictionary.yml"

    data = _load_schema(schema)
    objects: Dict[str, Dict[str, Any]] = {}
    for item in data.get("objects", []):
        objects[str(item["id"])] = {
            "name": item["objl"],
            "label": item.get("label", []),
        }

    lights: Dict[str, str] = {str(k): v for k, v in data.get("lights", {}).items()}

    if db_path is not None:
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.execute("SELECT code, text FROM light_codes")
            for code, text in cur.fetchall():
                lights[str(code)] = text
        finally:
            conn.close()

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump({"objects": objects, "lights": lights}, f, separators=(",", ":"))
    return output


if __name__ == "__main__":  # pragma: no cover
    build()
