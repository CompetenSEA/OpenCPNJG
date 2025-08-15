"""FastAPI service exposing chart tiles.

Endpoints:
    /tiles/{z}/{x}/{y}?fmt=png&pal=day
    /metrics

Tiles are cached in memory using an LRU strategy and optionally in Redis when
`REDIS_URL` is set.  Prometheus metrics record tile generation times and cache
hits.
"""
from __future__ import annotations

from functools import lru_cache
import math
import os
import charts_py
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

try:  # pragma: no cover - redis is optional
    import redis
except Exception:  # pragma: no cover
    redis = None

app = FastAPI()

_tile_gen_ms = Histogram("tile_gen_ms", "Time spent generating tiles", unit="ms")
_cache_hits = Counter("cache_hits", "Cache hits")
_redis = redis.from_url(os.environ["REDIS_URL"]) if redis and "REDIS_URL" in os.environ else None

def _tile_bounds(x: int, y: int, z: int) -> list[float]:
    n = 2 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return [lon_left, lat_bottom, lon_right, lat_top]

def _cache_key(z: int, x: int, y: int, fmt: str, pal: str) -> str:
    return f"{fmt}:{pal}:{z}/{x}/{y}"

@lru_cache(maxsize=512)
def _render_tile(bbox_tuple: tuple[float, float, float, float], z: int, fmt: str, pal: str) -> bytes:
    with _tile_gen_ms.time():
        return charts_py.generate_tile(list(bbox_tuple), z, fmt=fmt, palette=pal)

@app.get("/tiles/{z}/{x}/{y}")
def get_tile(z: int, x: int, y: int, fmt: str = "png", pal: str = "day") -> Response:
    key = _cache_key(z, x, y, fmt, pal)
    if _redis:
        cached = _redis.get(key)
        if cached:
            _cache_hits.inc()
            media = "image/png" if fmt == "png" else "application/x-protobuf"
            return Response(content=cached, media_type=media)

    bbox = _tile_bounds(x, y, z)
    data = _render_tile(tuple(bbox), z, fmt, pal)

    if _redis:
        _redis.set(key, data)

    media_type = "image/png" if fmt == "png" else "application/x-protobuf"
    return Response(content=data, media_type=media_type)

@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
