from __future__ import annotations
try:
    # prefer Django’s bindings if present
    from django.contrib.gis import gdal as dj_gdal  # type: ignore
    gdal = dj_gdal
    HAS_GDAL = True
except Exception:
    try:
        from osgeo import gdal as _gdal  # type: ignore
        gdal = _gdal
        HAS_GDAL = True
    except Exception:
        gdal = None
        HAS_GDAL = False
