from __future__ import annotations

import base64
import os
import time
from collections import OrderedDict
from typing import Tuple

from fastapi import FastAPI, Request, Response

from .metrics import (
    REGISTRY,
    CONTENT_TYPE_LATEST,
    generate_latest,
    tile_render_seconds,
    tile_bytes_total,
)

app = FastAPI()

# ---------------------------------------------------------------------------
# Simple in-process LRU cache
# ---------------------------------------------------------------------------
_CACHE_SIZE = int(os.environ.get("TILE_CACHE_SIZE", "64"))
_tile_cache: "OrderedDict[Tuple[int,int,int], bytes]" = OrderedDict()

# 1x1 transparent PNG
PNG_1X1 = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jP1kAAAAASUVORK5CYII="
)


@app.middleware("http")
async def _metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    if request.url.path.startswith("/tiles/"):
        elapsed = time.perf_counter() - start
        tile_render_seconds.labels(kind="tile").observe(elapsed)
    return response


def _cache_key(z: int, x: int, y: int) -> Tuple[int, int, int]:
    return z, x, y


@app.get("/tiles/{z}/{x}/{y}.png")
def get_tile(z: int, x: int, y: int) -> Response:
    key = _cache_key(z, x, y)
    data = _tile_cache.get(key)
    if data is None:
        data = PNG_1X1
        _tile_cache[key] = data
        _tile_cache.move_to_end(key)
        if len(_tile_cache) > _CACHE_SIZE:
            _tile_cache.popitem(last=False)
    else:
        _tile_cache.move_to_end(key)
    tile_bytes_total.labels(kind="tile").inc(len(data))
    return Response(data, media_type="image/png")


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
