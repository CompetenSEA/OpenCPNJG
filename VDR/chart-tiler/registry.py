"""Light‑weight chart registry with caching.

The real project uses a richer catalogue; for tests we only implement the
features required by the API endpoints.  Records are persisted to a small
SQLite database on disk so the registry can be shared between processes.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

DB_PATH = Path(__file__).with_name("registry.sqlite")
TTL_SEC = 300


@dataclass
class ChartRecord:
    id: str
    kind: str
    name: str
    bbox: List[float]
    minzoom: int
    maxzoom: int
    updatedAt: float
    path: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] | None = None


class Registry:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()
        self._cache_ts = 0.0
        self._cache: List[ChartRecord] = []

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS charts (
                id TEXT PRIMARY KEY,
                kind TEXT,
                name TEXT,
                bbox TEXT,
                minzoom INTEGER,
                maxzoom INTEGER,
                updated_at REAL,
                path TEXT,
                url TEXT,
                tags TEXT
            )
            """
        )
        self.conn.commit()

    # -- scanning -----------------------------------------------------------------
    def scan(self, paths: Iterable[Path]) -> None:
        """Scan provided directories for chart artefacts."""
        cur = self.conn.cursor()
        now = time.time()
        for p in paths:
            if not Path(p).exists():
                continue
            for mb in p.rglob("*.mbtiles"):
                rid = mb.stem
                # read bounds/minzoom/maxzoom from metadata table if available
                try:
                    mconn = sqlite3.connect(mb)
                    mcur = mconn.cursor()
                    meta = dict(mcur.execute("SELECT name,value FROM metadata").fetchall())
                    bbox = list(map(float, meta.get("bounds", "0,0,0,0").split(",")))
                    minzoom = int(meta.get("minzoom", 0))
                    maxzoom = int(meta.get("maxzoom", 0))
                    name = meta.get("name", rid)
                finally:
                    mconn.close()
                cur.execute(
                    "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,path) VALUES (?,?,?,?,?,?,?,?)",
                    (rid, "enc", name, json.dumps(bbox), minzoom, maxzoom, now, str(mb)),
                )
            for cog in p.rglob("*.cog.json"):
                rid = cog.stem.replace(".cog", "")
                info = json.loads(cog.read_text())
                bbox = info.get("bbox", [0, 0, 0, 0])
                minzoom = 0
                maxzoom = 0
                cur.execute(
                    "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,path) VALUES (?,?,?,?,?,?,?,?)",
                    (
                        rid,
                        "geotiff",
                        rid,
                        json.dumps(bbox),
                        minzoom,
                        maxzoom,
                        now,
                        str(cog.with_suffix(".tif")),
                    ),
                )
        if bool(int(os.environ.get("OSM_USE_COMMUNITY", "1"))):
            cur.execute(
                "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,url) VALUES (?,?,?,?,?,?,?,?)",
                (
                    "osm",
                    "osm",
                    "OpenStreetMap",
                    json.dumps([-180, -90, 180, 90]),
                    0,
                    19,
                    now,
                    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                ),
            )
        self.conn.commit()
        self._cache_ts = 0.0  # invalidate cache

    # -- queries ------------------------------------------------------------------
    def _refresh_cache(self) -> None:
        if time.time() - self._cache_ts < TTL_SEC:
            return
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT id,kind,name,bbox,minzoom,maxzoom,updated_at,path,url,tags FROM charts"
        ).fetchall()
        self._cache = [
            ChartRecord(
                id=row[0],
                kind=row[1],
                name=row[2],
                bbox=json.loads(row[3]),
                minzoom=row[4],
                maxzoom=row[5],
                updatedAt=row[6],
                path=row[7],
                url=row[8],
                tags=json.loads(row[9]) if row[9] else None,
            )
            for row in rows
        ]
        self._cache_ts = time.time()

    def list(self, kind: Optional[str] = None, q: Optional[str] = None, page: int = 1, pageSize: int = 50) -> List[ChartRecord]:
        self._refresh_cache()
        items = self._cache
        if kind:
            items = [i for i in items if i.kind == kind]
        if q:
            items = [i for i in items if q.lower() in i.name.lower()]
        start = (page - 1) * pageSize
        end = start + pageSize
        return items[start:end]

    def get(self, id: str) -> Optional[ChartRecord]:
        self._refresh_cache()
        for item in self._cache:
            if item.id == id:
                return item
        return None


_registry: Registry | None = None


def get_registry() -> Registry:
    global _registry
    if not _registry:
        _registry = Registry()
    return _registry
