from __future__ import annotations
import mimetypes
from typing import Optional

from ingest_pkg.compat import gdal, HAS_GDAL


def sniff_raster(path: str) -> Optional[str]:
    """Return a short driver name for raster files.

    Uses GDAL when available, otherwise falls back to mime-type based
    guessing. Returns ``None`` if nothing can be determined.
    """
    if HAS_GDAL and gdal is not None:
        try:
            ds = gdal.Open(path)  # type: ignore[attr-defined]
            if ds:
                drv = ds.GetDriver()
                return getattr(drv, "ShortName", None)
        except Exception:
            return None
    # fallback
    mime, _ = mimetypes.guess_type(path)
    return mime
