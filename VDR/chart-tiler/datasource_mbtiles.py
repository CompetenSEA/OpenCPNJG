"""Tiny helper around MBTiles used for tests and the dev tile server."""

import os
import sqlite3
from functools import lru_cache
from typing import Optional, Dict


class MBTilesDataSource:
    """Lightweight reader for MBTiles storing Mapbox Vector Tiles.

    The interface intentionally stays very small: :meth:`get_tile` returns the
    raw tile bytes for ``(z, x, y)`` if present.  Metadata from the ``metadata``
    table is exposed via :meth:`metadata` for informational endpoints.  A tiny
    in‑process LRU cache keeps recently used tiles in memory; the cache size can
    be tuned via the ``MBTILES_CACHE_SIZE`` environment variable.
    """

    def __init__(self, path: str, cache_size: int | None = None) -> None:
        self.path = path
        # ``check_same_thread=False`` allows usage from FastAPI threads.
        self._conn = sqlite3.connect(path, check_same_thread=False)

        size = cache_size or int(os.environ.get("MBTILES_CACHE_SIZE", "1024"))

        # lru_cache needs to wrap a function defined at runtime so we create an
        # instance specific accessor which forwards to the real implementation.
        self._cached_get = lru_cache(maxsize=size)(self._get_tile_uncached)

    # -- metadata ---------------------------------------------------------
    def metadata(self) -> Dict[str, str]:
        cur = self._conn.execute("SELECT name, value FROM metadata")
        return {name: value for name, value in cur.fetchall()}

    def summary(self) -> Dict[str, object]:
        meta = self.metadata()
        return {
            "name": meta.get("name"),
            "bounds": meta.get("bounds"),
            "minzoom": int(meta.get("minzoom", 0)),
            "maxzoom": int(meta.get("maxzoom", 0)),
        }

    # -- tiles ------------------------------------------------------------
    def _get_tile_uncached(self, z: int, x: int, y: int) -> Optional[bytes]:
        tms_y = (2 ** z - 1) - y  # MBTiles stores TMS scheme
        cur = self._conn.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (z, x, tms_y),
        )
        row = cur.fetchone()
        return row[0] if row else None

    def get_tile(self, z: int, x: int, y: int) -> Optional[bytes]:
        """Return raw tile bytes for ``z/x/y`` or ``None`` if missing."""

        return self._cached_get(z, x, y)
