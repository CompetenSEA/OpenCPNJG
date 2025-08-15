"""FastAPI service exposing raster or vector chart tiles.

The application provides two HTTP endpoints:

``/tiles/{z}/{x}/{y}``
    Returns a tile in either PNG or Mapbox Vector Tile (``fmt=mvt``) format.
    Tiles are cached using an in‑process LRU cache and optionally in Redis when
    ``REDIS_URL`` is defined.  Both caches are tracked via Prometheus metrics.

``/metrics``
    Exposes Prometheus metrics including ``tile_gen_ms`` (time spent
    generating tiles) and ``cache_hits``.
"""
from __future__ import annotations

from functools import lru_cache
import math
import os
import time
import logging
from typing import Optional

import charts_py
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

try:  # pragma: no cover - redis is optional
    import redis
except Exception:  # pragma: no cover
    redis = None

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
logger = logging.getLogger("tileserver")

_tile_gen_ms = Histogram("tile_gen_ms", "Time spent generating tiles", unit="ms")
_cache_hits = Counter("cache_hits", "Cache hits")
_redis: Optional["redis.Redis"] = (
    redis.from_url(os.environ["REDIS_URL"]) if redis and "REDIS_URL" in os.environ else None
)
_redis_ttl = int(os.environ.get("REDIS_TTL", "0"))  # seconds; 0 means no expiry


def _tile_bounds(x: int, y: int, z: int) -> list[float]:
    """Return the Web‑Mercator bounding box for a given tile."""

    n = 2 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return [lon_left, lat_bottom, lon_right, lat_top]


def _cache_key(z: int, x: int, y: int, fmt: str, pal: str, safety: float) -> str:
    """Return a unique cache key for a tile request."""

    return f"{fmt}:{pal}:{safety}:{z}/{x}/{y}"


@lru_cache(maxsize=512)
def _render_tile(
    bbox_tuple: tuple[float, float, float, float],
    z: int,
    fmt: str,
    pal: str,
    safety: float,
) -> bytes:
    """Invoke :func:`charts_py.generate_tile` with Prometheus timing."""

    opts = {"format": fmt, "palette": pal, "safetyContour": safety}
    with _tile_gen_ms.time():
        return charts_py.generate_tile(list(bbox_tuple), z, opts)

@app.get("/tiles/cm93/{z}/{x}/{y}")
def get_tile(
    z: int,
    x: int,
    y: int,
    fmt: str = "png",
    palette: str = "day",
    safetyContour: float = 0.0,
) -> Response:
    """Return a single chart tile.

    Parameters mirror :func:`charts_py.generate_tile`.  When Redis is configured
    tiles are stored with an optional TTL specified via ``REDIS_TTL``.
    """

    key = _cache_key(z, x, y, fmt, palette, safetyContour)
    cache_status = "miss"
    if _redis:
        cached = _redis.get(key)
        if cached:
            cache_status = "hit"
            _cache_hits.inc()
            media = "image/png" if fmt == "png" else "application/x-protobuf"
            logger.info(
                "tile_request",
                extra={
                    "z": z,
                    "x": x,
                    "y": y,
                    "fmt": fmt,
                    "palette": palette,
                    "safetyContour": safetyContour,
                    "cache": cache_status,
                    "ms": 0.0,
                },
            )
            return Response(content=cached, media_type=media)

    bbox = _tile_bounds(x, y, z)
    info_before = _render_tile.cache_info()
    start = time.perf_counter()
    data = _render_tile(tuple(bbox), z, fmt, palette, safetyContour)
    ms = (time.perf_counter() - start) * 1000
    info_after = _render_tile.cache_info()
    if info_after.hits > info_before.hits:
        cache_status = "hit"
        _cache_hits.inc()

    if _redis:
        _redis.set(key, data, ex=_redis_ttl or None)

    logger.info(
        "tile_request",
        extra={
            "z": z,
            "x": x,
            "y": y,
            "fmt": fmt,
            "palette": palette,
            "safetyContour": safetyContour,
            "cache": cache_status,
            "ms": ms,
        },
    )

    media_type = "image/png" if fmt == "png" else "application/x-protobuf"
    return Response(content=data, media_type=media_type)

@app.get("/metrics")
def metrics() -> Response:
    """Return Prometheus metrics in the text exposition format."""

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
