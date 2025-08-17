"""Light‑weight chart registry with caching.

Usage
-----
>>> python -m registry PATH [PATH ...]

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
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Dict

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
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    senc_path: Optional[str] = None


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
                tags TEXT,
                scale_min INTEGER,
                scale_max INTEGER,
                senc_path TEXT
            )
            """
        )
        self.conn.commit()

    def register_mbtiles(self, meta_path: Path, tiles_path: Path) -> None:
        info = json.loads(Path(meta_path).read_text())
        rid = tiles_path.stem
        bbox = info.get("bounds", [0, 0, 0, 0])
        minzoom = int(info.get("minzoom", 0))
        maxzoom = int(info.get("maxzoom", 0))
        kind = info.get("kind", "enc")
        name = info.get("name", rid)
        ts = time.time()
        if isinstance(info.get("updatedAt"), str):
            try:
                ts = datetime.fromisoformat(info["updatedAt"]).timestamp()
            except Exception:
                pass
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,path) VALUES (?,?,?,?,?,?,?,?)",
            (rid, kind, name, json.dumps(bbox), minzoom, maxzoom, ts, str(tiles_path)),
        )
        self.conn.commit()

    def register_cog(self, meta_path: Path, cog_path: Path) -> None:
        info = json.loads(Path(meta_path).read_text())
        rid = cog_path.stem.replace(".cog", "")
        bbox = info.get("bbox", [0, 0, 0, 0])
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,path) VALUES (?,?,?,?,?,?,?,?)",
            (
                rid,
                "geotiff",
                rid,
                json.dumps(bbox),
                0,
                0,
                time.time(),
                str(cog_path),
            ),
        )
        self.conn.commit()

    def register_senc(self, meta_path: Path, senc_path: Path) -> None:
        info = json.loads(Path(meta_path).read_text())
        rid = senc_path.stem
        bbox = info.get("bbox", [0, 0, 0, 0])
        scale_min = int(info.get("scale_min", 0))
        scale_max = int(info.get("scale_max", 0))
        name = info.get("name", rid)
        ts = time.time()
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,scale_min,scale_max,senc_path) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                rid,
                "senc",
                name,
                json.dumps(bbox),
                0,
                0,
                ts,
                scale_min,
                scale_max,
                str(senc_path),
            ),
        )
        self.conn.commit()

    def register_cm93(self, meta_path: Path, db_path: Path) -> None:
        info = json.loads(Path(meta_path).read_text())
        rid = db_path.stem
        bbox = info.get("bbox", [0, 0, 0, 0])
        scale_min = int(info.get("scale_min", 0))
        scale_max = int(info.get("scale_max", 0))
        name = info.get("name", rid)
        ts = time.time()
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO charts (id,kind,name,bbox,minzoom,maxzoom,updated_at,scale_min,scale_max,path) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (rid, "cm93", name, json.dumps(bbox), 0, 0, ts, scale_min, scale_max, str(db_path)),
        )
        self.conn.commit()

    # -- scanning -----------------------------------------------------------------
    def scan(self, paths: Iterable[Path]) -> None:
        """Scan provided directories for chart artefacts."""
        cur = self.conn.cursor()
        for p in paths:
            if not Path(p).exists():
                continue
            for meta in p.rglob("*.meta.json"):
                mb = meta.with_name(meta.name.replace(".meta.json", ".mbtiles"))
                if mb.exists():
                    self.register_mbtiles(meta, mb)
            for cog_meta in p.rglob("*.cog.json"):
                cog = cog_meta.with_suffix(".tif")
                if cog.exists():
                    self.register_cog(cog_meta, cog)
            for senc_meta in p.rglob("*.senc.json"):
                base = senc_meta.name.replace(".senc.json", "")
                senc = senc_meta.with_name(f"{base}.senc")
                if senc.exists():
                    self.register_senc(senc_meta, senc)
            for mb in p.rglob("*.mbtiles"):
                if mb.with_suffix(".meta.json").exists():
                    continue
                rid = mb.stem
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
                    (rid, "enc", name, json.dumps(bbox), minzoom, maxzoom, time.time(), str(mb)),
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
                    time.time(),
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
            "SELECT id,kind,name,bbox,minzoom,maxzoom,updated_at,path,url,tags,scale_min,scale_max,senc_path FROM charts ORDER BY updated_at DESC"
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
                scale_min=row[10],
                scale_max=row[11],
                senc_path=row[12],
            )
            for row in rows
        ]
        self._cache_ts = time.time()

    def list(self, kind: Optional[str] = None, q: Optional[str] = None, page: int = 1, pageSize: int = 50) -> List[ChartRecord]:
        self._refresh_cache()
        items = [i for i in self._cache if i.kind in {"enc", "cm93", "geotiff", "osm"}]
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


# ---------------------------------------------------------------------------
# ENC dataset discovery
# ---------------------------------------------------------------------------

@dataclass
class Dataset:
    id: str
    title: str
    path: Path
    bounds: List[float]
    minzoom: int
    maxzoom: int
    updated_at: float


_enc_cache: Dict[Path, tuple[float, List[Dataset]]] = {}


def _enc_dir(enc_dir: Optional[Path] = None) -> Path:
    base = Path(__file__).resolve().parent / "data" / "enc"
    return Path(os.environ.get("ENC_DIR", enc_dir or base))


def _scan_enc(dir_path: Path) -> List[Dataset]:
    datasets: List[Dataset] = []
    for mb in sorted(dir_path.glob("*.mbtiles")):
        try:
            conn = sqlite3.connect(mb)
            cur = conn.cursor()
            meta = dict(cur.execute("SELECT name,value FROM metadata").fetchall())
        finally:
            conn.close()
        bounds = [float(x) for x in meta.get("bounds", "0,0,0,0").split(",")]
        minzoom = int(meta.get("minzoom", 0))
        maxzoom = int(meta.get("maxzoom", 0))
        title = meta.get("name", mb.stem)
        datasets.append(
            Dataset(
                id=mb.stem,
                title=title,
                path=mb,
                bounds=bounds,
                minzoom=minzoom,
                maxzoom=maxzoom,
                updated_at=mb.stat().st_mtime,
            )
        )
    datasets.sort(key=lambda d: (d.title, d.id))
    return datasets


def list_datasets(enc_dir: Optional[Path] = None) -> List[Dataset]:
    """List ENC datasets (cached by directory mtime)."""

    dir_path = _enc_dir(enc_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    mtime = max((p.stat().st_mtime for p in dir_path.glob("*.mbtiles")), default=0)
    cached = _enc_cache.get(dir_path)
    if not cached or cached[0] < mtime:
        _enc_cache[dir_path] = (mtime, _scan_enc(dir_path))
    return list(_enc_cache[dir_path][1])


def get_dataset(ds_id: str, enc_dir: Optional[Path] = None) -> Dataset | None:
    """Return dataset by id or ``None`` if missing."""

    for ds in list_datasets(enc_dir):
        if ds.id == ds_id:
            return ds
    return None


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Directories to scan")
    args = parser.parse_args()
    Registry().scan(args.paths)
