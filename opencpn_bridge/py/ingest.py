import json
import sqlite3
from pathlib import Path

from .bridge import build_senc


def ingest_dataset(dataset_id: str, src_root: str, dataset_type: str) -> None:
    """Build a stub SENC for ``src_root`` and record it in the registry."""
    root = Path(__file__).resolve().parent.parent
    src_path = Path(src_root)
    senc_root = root / ".cache" / "senc" / dataset_id
    senc_root.mkdir(parents=True, exist_ok=True)

    build_senc(str(src_path), str(senc_root))

    provenance_path = senc_root / "provenance.json"
    bounds = minzoom = maxzoom = None
    if provenance_path.exists():
        with provenance_path.open() as f:
            data = json.load(f)
        bounds = data.get("bounds")
        minzoom = data.get("minzoom")
        maxzoom = data.get("maxzoom")

    if bounds is None:
        bounds = [0, 0, 0, 0]
    if minzoom is None:
        minzoom = 0
    if maxzoom is None:
        maxzoom = 0

    registry_path = root / "registry" / "registry.sqlite"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(registry_path)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS datasets(
                id TEXT PRIMARY KEY,
                type TEXT,
                bounds TEXT,
                minzoom INTEGER,
                maxzoom INTEGER,
                senc_path TEXT,
                provenance_path TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO datasets(id, type, bounds, minzoom, maxzoom, senc_path, provenance_path)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                type=excluded.type,
                bounds=excluded.bounds,
                minzoom=excluded.minzoom,
                maxzoom=excluded.maxzoom,
                senc_path=excluded.senc_path,
                provenance_path=excluded.provenance_path
            """,
            (
                dataset_id,
                dataset_type,
                json.dumps(bounds),
                minzoom,
                maxzoom,
                str(senc_root),
                str(provenance_path) if provenance_path.exists() else None,
            ),
        )
    conn.close()
