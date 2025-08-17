import json
import sqlite3
from pathlib import Path
from typing import Iterator, Dict, Any


def list_datasets() -> Iterator[Dict[str, Any]]:
    """Yield dataset records from ``registry.sqlite`` if available."""
    registry_path = Path(__file__).resolve().parent / "registry.sqlite"
    if not registry_path.exists():
        return

    conn = sqlite3.connect(registry_path)
    conn.row_factory = sqlite3.Row
    try:
        for row in conn.execute(
            "SELECT id, type, bounds, minzoom, maxzoom, senc_path, provenance_path FROM datasets"
        ):
            yield {
                "id": row["id"],
                "type": row["type"],
                "bounds": json.loads(row["bounds"]) if row["bounds"] else None,
                "minzoom": row["minzoom"],
                "maxzoom": row["maxzoom"],
                "senc_path": row["senc_path"],
                "provenance_path": row["provenance_path"],
            }
    finally:
        conn.close()
