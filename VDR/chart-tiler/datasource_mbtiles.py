import sqlite3
from functools import lru_cache
from typing import Optional, Dict


class MBTilesDataSource:
    """Lightweight reader for MBTiles storing Mapbox Vector Tiles.

    The class intentionally keeps the interface tiny: ``get_tile`` returns the
    raw tile bytes for ``(z, x, y)`` if present.  Metadata from the ``metadata``
    table is exposed via :meth:`metadata` for informational endpoints.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        # ``check_same_thread=False`` allows usage from FastAPI threads.
        self._conn = sqlite3.connect(path, check_same_thread=False)

    def metadata(self) -> Dict[str, str]:
        cur = self._conn.execute("SELECT name, value FROM metadata")
        return {name: value for name, value in cur.fetchall()}

    @lru_cache(maxsize=1024)
    def get_tile(self, z: int, x: int, y: int) -> Optional[bytes]:
        """Return raw tile bytes for ``z/x/y`` or ``None`` if missing."""

        tms_y = (2 ** z - 1) - y  # MBTiles stores TMS scheme
        cur = self._conn.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (z, x, tms_y),
        )
        row = cur.fetchone()
        return row[0] if row else None
