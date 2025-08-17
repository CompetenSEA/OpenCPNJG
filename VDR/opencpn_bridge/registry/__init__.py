from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class Dataset:
    id: str
    type: str
    bounds: Optional[List[float]]
    minzoom: int
    maxzoom: int
    senc_path: str
    provenance_path: str

    @property
    def title(self) -> str:  # read-only property
        return self.id


def list_datasets(db_path: Path | None = None) -> List[Dataset]:
    """Return datasets stored in ``registry.sqlite``.

    Parameters
    ----------
    db_path: Path | None
        Path to the registry database. Defaults to ``registry.sqlite`` next to this file.
    """
    if db_path is None:
        db_path = Path(__file__).resolve().parent / "registry.sqlite"
    if not db_path.exists():
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, type, bounds, minzoom, maxzoom, senc_path, provenance_path FROM datasets"
        )
        datasets: List[Dataset] = []
        for row in cursor:
            datasets.append(
                Dataset(
                    id=row["id"],
                    type=row["type"],
                    bounds=json.loads(row["bounds"]) if row["bounds"] else None,
                    minzoom=row["minzoom"],
                    maxzoom=row["maxzoom"],
                    senc_path=row["senc_path"],
                    provenance_path=row["provenance_path"],
                )
            )
        return datasets
    finally:
        conn.close()


__all__ = ["Dataset", "list_datasets"]
