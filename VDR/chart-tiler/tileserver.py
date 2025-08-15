"""Minimal FastAPI tile server used for tests and development.

The server intentionally returns placeholder data – a 1×1 PNG for raster tiles
and a tiny Mapbox Vector Tile containing a single point feature.  The goal is to
exercise the caching, routing and static file serving infrastructure without the
full chart rendering pipeline.
"""

from __future__ import annotations

import base64
import logging
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

try:  # pragma: no cover - redis optional
    import redis
except Exception:  # pragma: no cover
    redis = None

from mapbox_vector_tile import encode as mvt_encode


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
logger = logging.getLogger("tileserver")

_tile_gen_ms = Histogram("tile_gen_ms", "Time spent generating tiles", unit="ms")
_cache_hits = Counter("cache_hits", "Cache hits")
_redis: Optional["redis.Redis"] = (
    redis.from_url(os.environ["REDIS_URL"]) if redis and "REDIS_URL" in os.environ else None
)
_redis_ttl = int(os.environ.get("REDIS_TTL", "0"))

BASE_DIR = Path(__file__).resolve().parents[1]
STYLING_DIST = BASE_DIR / "server-styling" / "dist"

PNG_1X1 = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jP1kAAAAASUVORK5CYII="
)


def _cache_key(fmt: str, sc: float, z: int, x: int, y: int) -> str:
    return f"{fmt}:{sc}:{z}/{x}/{y}"


@lru_cache(maxsize=512)
def _render_mvt(sc: float, z: int, x: int, y: int) -> bytes:
    # Encode a single point feature with the required properties
    feature = {
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "properties": {
            "OBJL": "SOUNDG",
            "DRVAL1": 0.0,
            "DRVAL2": 0.0,
            "VALDCO": sc,
            "VALSOU": sc,
            "QUAPOS": 1,
        },
    }
    layer = {"name": "features", "features": [feature]}
    with _tile_gen_ms.time():
        return mvt_encode([layer])


@lru_cache(maxsize=512)
def _render_png(sc: float, z: int, x: int, y: int) -> bytes:  # pragma: no cover - trivial
    _ = (sc, z, x, y)  # unused, but part of cache key
    return PNG_1X1


def _get_from_redis(key: str) -> Optional[bytes]:  # pragma: no cover - depends on redis
    if _redis:
        cached = _redis.get(key)
        if cached:
            _cache_hits.inc()
            return cached
    return None


def _set_redis(key: str, value: bytes) -> None:  # pragma: no cover - depends on redis
    if _redis:
        _redis.set(key, value, ex=_redis_ttl or None)


@app.get("/tiles/cm93/{z}/{x}/{y}.png")
def tiles_png(z: int, x: int, y: str, sc: float = 0.0) -> Response:
    """Serve raster PNG tiles."""

    try:
        y_int = int(y)
    except ValueError:
        return Response(status_code=422)
    return tiles(z, x, y_int, fmt="png", sc=sc)


@app.get("/tiles/cm93/{z}/{x}/{y}")
def tiles(z: int, x: int, y: int, fmt: str = "mvt", sc: float = 0.0) -> Response:
    start = time.perf_counter()
    key = _cache_key(fmt, sc, z, x, y)
    cached = _get_from_redis(key)
    cache_state = "hit" if cached is not None else "miss"
    if cached is not None:
        media = "image/png" if fmt == "png" else "application/x-protobuf"
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "fmt=%s sc=%s z=%d x=%d y=%d cache=%s ms=%.2f",
            fmt,
            sc,
            z,
            x,
            y,
            cache_state,
            duration_ms,
        )
        return Response(content=cached, media_type=media)

    if fmt == "png":
        data = _render_png(sc, z, x, y)
        media_type = "image/png"
    else:
        data = _render_mvt(sc, z, x, y)
        media_type = "application/x-protobuf"

    _set_redis(key, data)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "fmt=%s sc=%s z=%d x=%d y=%d cache=%s ms=%.2f",
        fmt,
        sc,
        z,
        x,
        y,
        cache_state,
        duration_ms,
    )
    return Response(content=data, media_type=media_type)


@app.get("/style/s52.day.json")
def style() -> Response:
    path = STYLING_DIST / "style.s52.day.json"
    return Response(path.read_bytes(), media_type="application/json")


@app.get("/sprites/s52-day.json")
def sprite_json() -> Response:
    path = STYLING_DIST / "sprites" / "s52-day.json"
    return Response(path.read_bytes(), media_type="application/json")


@app.get("/sprites/s52-day.png")
def sprite_png() -> Response:
    path = STYLING_DIST / "assets" / "s52" / "rastersymbols-day.png"
    return Response(path.read_bytes(), media_type="image/png")


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

