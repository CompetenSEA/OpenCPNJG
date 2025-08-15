"""Minimal FastAPI tile server used for tests and development.

The server intentionally returns placeholder data – a 1×1 PNG for raster tiles
and a tiny Mapbox Vector Tile containing a single point feature.  The goal is to
exercise the caching, routing and static file serving infrastructure without the
full chart rendering pipeline.
"""

from __future__ import annotations

import base64
import logging
import math
import os
import sys
import time
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

try:  # pragma: no cover - redis optional
    import redis
except Exception:  # pragma: no cover
    redis = None

from datasource_stub import features_for_tile
from mvt_builder import encode_mvt
from s52_preclass import S52PreClassifier

# Allow importing parsing helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server-styling"))
from s52_xml import parse_day_colors, parse_symbols


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


def _tile_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    n = 2.0 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi - 2.0 * math.pi * y / n)))
    lat_bottom = math.degrees(
        math.atan(math.sinh(math.pi - 2.0 * math.pi * (y + 1) / n))
    )
    return lon_left, lat_bottom, lon_right, lat_top


_chartsymbols_path = STYLING_DIST / "assets" / "s52" / "chartsymbols.xml"
_root = ET.parse(_chartsymbols_path).getroot()
_day_colors = parse_day_colors(_root)
_symbols = parse_symbols(_root)


@lru_cache(maxsize=32)
def _get_classifier(sc: float) -> S52PreClassifier:
    return S52PreClassifier(sc, _day_colors, _symbols)


@lru_cache(maxsize=512)
def _render_mvt(sc: float, z: int, x: int, y: int) -> bytes:
    """Build a Mapbox Vector Tile for the requested tile."""

    bbox = _tile_bbox(z, x, y)
    classifier = _get_classifier(sc)

    feats = []
    for feat in features_for_tile(bbox, z, x, y):
        props = dict(feat.get("properties", {}))
        objl = props.get("OBJL", "")
        props.update(classifier.classify(objl, props))
        feats.append({"geometry": feat["geometry"], "properties": props})

    with _tile_gen_ms.time():
        return encode_mvt(feats)


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
        return Response(
            content=cached, media_type=media, headers={"X-Tile-Cache": cache_state}
        )

    if fmt == "png":
        before = _render_png.cache_info().hits
        data = _render_png(sc, z, x, y)
        after = _render_png.cache_info().hits
        media_type = "image/png"
    else:
        before = _render_mvt.cache_info().hits
        data = _render_mvt(sc, z, x, y)
        after = _render_mvt.cache_info().hits
        media_type = "application/x-protobuf"
    if after > before:
        cache_state = "hit"
        _cache_hits.inc()

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
    return Response(content=data, media_type=media_type, headers={"X-Tile-Cache": cache_state})


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

