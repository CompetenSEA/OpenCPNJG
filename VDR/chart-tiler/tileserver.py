"""Minimal FastAPI tile server used for tests and development.

The server returns deterministic placeholder data for CM93 tiles and serves
ENC vector tiles by querying a lightweight OpenCPN bridge.  Features are
pre‑classified using a tiny subset of S‑52 rules and encoded to Mapbox Vector
Tiles.  Middleware enables CORS and gzip; tile responses carry `ETag` and
`Cache-Control` headers to exercise caching, routing and static file serving
without the full rendering pipeline.
"""

from __future__ import annotations

import base64
import json
import logging
import math
import os
import sys
import time
import xml.etree.ElementTree as ET
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
import hashlib
import resource
import sqlite3
from registry import get_registry, ChartRecord, list_datasets, get_dataset
from typing import Dict, Optional, List, Any

try:
    from rio_tiler.io import Reader  # type: ignore
except Exception:  # pragma: no cover
    Reader = None

from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from prometheus_client import Counter
from metrics import (
    REGISTRY,
    CONTENT_TYPE_LATEST,
    generate_latest,
    tile_render_seconds,
    tile_bytes_total,
    tile_size_bytes,
    process_resident_memory_bytes,
)

try:  # pragma: no cover - redis optional
    import redis
except Exception:  # pragma: no cover
    redis = None

try:
    from opencpn_bridge import query_features
except Exception:  # pragma: no cover - optional dependency
    def query_features(handle, bbox, scale):  # type: ignore
        return []
from mvt_builder import encode_mvt
from s52_preclass import S52PreClassifier, ContourConfig
from cm93_rules import apply_scamin
from lights import build_light_sectors, build_light_character
from shapely.geometry import Point, mapping
from dict_builder import _MAPPING as _DICT_MAPPING
try:  # pragma: no cover - optional pillow
    from raster_mvp import render_tile as render_raster, RasterMVPUnavailable
except Exception:  # pragma: no cover
    render_raster = None  # type: ignore
    class RasterMVPUnavailable(Exception):
        pass

# Allow importing parsing helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server-styling"))
from s52_xml import parse_day_colors, parse_symbols


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(GZipMiddleware, minimum_size=512)
logger = logging.getLogger("tileserver")


@app.exception_handler(HTTPException)
async def _http_exc_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": exc.detail or "error"}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def _exc_handler(_: Request, exc: Exception) -> JSONResponse:  # pragma: no cover - defensive
    logger.exception("unhandled error: %s", exc)
    return JSONResponse({"error": "internal server error"}, status_code=500)

_prom_registry = REGISTRY
if "_cache_hits" not in globals():
    _cache_hits = Counter("cache_hits", "Cache hits", registry=_prom_registry)
_redis: Optional["redis.Redis"] = (
    redis.from_url(os.environ["REDIS_URL"]) if redis and "REDIS_URL" in os.environ else None
)
_redis_ttl = int(os.environ.get("REDIS_TTL", "0"))


def _rss_bytes() -> int:
    """Return current process resident memory in bytes."""
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except Exception:  # pragma: no cover - platform specific
        return 0
    # Linux reports kilobytes, macOS bytes
    return usage if sys.platform == "darwin" else usage * 1024


@app.middleware("http")
async def _metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    path = request.url.path
    kind: Optional[str] = None
    if path.startswith("/tiles/cm93-core"):
        kind = "cm93-core"
    elif path.startswith("/tiles/cm93-label"):
        kind = "cm93-label"
    elif path.startswith("/tiles/geotiff"):
        kind = "geotiff"
    if kind:
        tile_render_seconds.labels(kind=kind).observe(time.perf_counter() - start)
        body = getattr(response, "body", b"")
        size = len(body)
        tile_bytes_total.labels(kind=kind).inc(size)
        tile_size_bytes.labels(kind=kind).set(size)
        process_resident_memory_bytes.set(_rss_bytes())
    return response

BASE_DIR = Path(__file__).resolve().parents[1]
STYLING_DIST = BASE_DIR / "server-styling" / "dist"

PNG_1X1 = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jP1kAAAAASUVORK5CYII="
)



def _cache_key(fmt: str, cfg: ContourConfig, z: int, x: int, y: int, ds: str = "") -> str:
    """Return a cache key incorporating format, dataset and mariner params."""

    mariner = f"{cfg.safety},{cfg.shallow},{cfg.deep}"
    return f"{fmt}:{ds}:{z}/{x}/{y}:{mariner}"


def _tile_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    n = 2.0 ** z
    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0
    lat_top = math.degrees(math.atan(math.sinh(math.pi - 2.0 * math.pi * y / n)))
    lat_bottom = math.degrees(
        math.atan(math.sinh(math.pi - 2.0 * math.pi * (y + 1) / n))
    )
    return lon_left, lat_bottom, lon_right, lat_top


def _cfg_from_params(
    sc: float | None,
    safety: float | None,
    shallow: float | None,
    deep: float | None,
) -> ContourConfig:
    if safety is not None or shallow is not None or deep is not None:
        return ContourConfig(
            safety=safety if safety is not None else DEFAULT_CONFIG.safety,
            shallow=shallow if shallow is not None else DEFAULT_CONFIG.shallow,
            deep=deep if deep is not None else DEFAULT_CONFIG.deep,
        )
    if sc is not None:
        return ContourConfig(safety=sc, shallow=sc, deep=sc)
    return DEFAULT_CONFIG


_chartsymbols_path = STYLING_DIST / "assets" / "s52" / "chartsymbols.xml"
try:
    _root = ET.parse(_chartsymbols_path).getroot()
    _day_colors = parse_day_colors(_root)
    _symbols = parse_symbols(_root)
except FileNotFoundError:
    _root = ET.Element("root")
    _day_colors = {}
_symbols = {}
DEFAULT_CONFIG = ContourConfig()

# Reverse lookup for compact object codes used in tiles
_OBJL_CODES: Dict[str, int] = {v: k for k, v in _DICT_MAPPING.items()}


@lru_cache(maxsize=32)
def _get_classifier(cfg: ContourConfig) -> S52PreClassifier:
    return S52PreClassifier(cfg, _day_colors, symbols=_symbols)


def _rect_polygon(x1: float, y1: float, x2: float, y2: float) -> List[List[List[float]]]:
    """Return coordinates for a simple rectangle polygon."""

    return [[[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]]]


def features_for_tile(bbox, z: int, x: int, y: int) -> List[Dict[str, Any]]:
    """Yield deterministic features for the given tile.

    This mirrors the behaviour of the previous datasource_stub module so tests
    remain deterministic for CM93 placeholder tiles.
    """

    minx, miny, maxx, maxy = bbox
    midx = (minx + maxx) / 2.0
    midy = (miny + maxy) / 2.0

    feats: List[Dict[str, Any]] = []
    feats.append(
        {
            "geometry": {"type": "Polygon", "coordinates": _rect_polygon(minx, miny, midx, maxy)},
            "properties": {"OBJL": "LNDARE"},
        }
    )
    feats.append(
        {
            "geometry": {"type": "Polygon", "coordinates": _rect_polygon(midx, miny, maxx, midy)},
            "properties": {"OBJL": "DEPARE", "DRVAL1": 0.0, "DRVAL2": 5.0},
        }
    )
    feats.append(
        {
            "geometry": {"type": "Polygon", "coordinates": _rect_polygon(midx, midy, maxx, maxy)},
            "properties": {"OBJL": "DEPARE", "DRVAL1": 10.0, "DRVAL2": 100.0},
        }
    )
    vals = [5.0, 10.0, 15.0]
    for i, v in enumerate(vals):
        x_coord = midx + (i + 1) * (maxx - midx) / 4.0
        feats.append(
            {
                "geometry": {"type": "LineString", "coordinates": [[x_coord, miny], [x_coord, maxy]]},
                "properties": {
                    "OBJL": "DEPCNT",
                    "VALDCO": v,
                    "QUAPOS": 3 if i == 1 else 1,
                },
            }
        )
    feats.append(
        {
            "geometry": {"type": "LineString", "coordinates": [[midx, miny], [midx, maxy]]},
            "properties": {"OBJL": "COALNE"},
        }
    )
    sound_vals = [2.0, 15.0]
    for i, val in enumerate(sound_vals):
        sx = midx + (i + 1) * (maxx - midx) / 3.0
        sy = miny + (i + 1) * (maxy - miny) / 3.0
        feats.append(
            {
                "geometry": {"type": "Point", "coordinates": [sx, sy]},
                "properties": {"OBJL": "SOUNDG", "VALSOU": val},
            }
        )
    hx = midx + (maxx - midx) / 2.0
    hy = midy
    feats.append(
        {
            "geometry": {"type": "Point", "coordinates": [hx, hy]},
            "properties": {"OBJL": "WRECKS", "VALSOU": 3.0},
        }
    )
    feats.append(
        {
            "geometry": {"type": "Point", "coordinates": [hx, hy + (maxy - midy) / 4.0]},
            "properties": {"OBJL": "OBSTRN", "VALSOU": 20.0},
        }
    )
    return feats


def _build_features(cfg: ContourConfig, z: int, x: int, y: int) -> List[Dict[str, Any]]:
    bbox = _tile_bbox(z, x, y)
    classifier = _get_classifier(cfg)

    feats: List[Dict[str, Any]] = []
    contours: List[Dict[str, Any]] = []
    for feat in features_for_tile(bbox, z, x, y):
        props = dict(feat.get("properties", {}))
        objl = props.get("OBJL", "")
        if objl == "LIGHTS":
            if not apply_scamin(objl, z):
                continue
            sector = build_light_sectors(Point(feat["geometry"]["coordinates"]), props)
            if sector.geom_type == "MultiPolygon":
                exterior = list(sector.geoms[0].exterior.coords)[:2]
                geom = {"type": "LineString", "coordinates": exterior}
            else:
                geom = json.loads(json.dumps(mapping(sector)))
            feats.append(
                {
                    "geometry": geom,
                    "properties": {"OBJL": _OBJL_CODES.get("LIGHTS", 0)},
                    "id": len(feats) + 1,
                }
            )
            code = build_light_character(props)
            feats.append(
                {
                    "geometry": feat["geometry"],
                    "properties": {"OBJL": _OBJL_CODES.get("LIGHTS", 0), "text": code},
                }
            )
            continue
        if not apply_scamin(objl, z):
            continue
        props.update(classifier.classify(objl, props))
        props["OBJL"] = _OBJL_CODES.get(objl, 0)
        feat_dict = {"geometry": feat["geometry"], "properties": props}
        feats.append(feat_dict)
        if objl == "DEPCNT":
            contours.append(feat_dict)
    mark = S52PreClassifier.finalize_tile(contours, cfg)
    for idx in mark:
        props = contours[idx]["properties"]
        props["role"] = "safety"
        props["isSafety"] = True
    return feats


@lru_cache(maxsize=512)
def _render_mvt(cfg: ContourConfig, z: int, x: int, y: int) -> bytes:
    """Build a Mapbox Vector Tile for the requested tile."""
    feats = _build_features(cfg, z, x, y)
    return encode_mvt(feats)


# SQLite-backed helpers used in tests to mimic the PostGIS SQL functions.
_db = sqlite3.connect(":memory:", check_same_thread=False)


def _cm93_mvt_core_py(z: int, x: int, y: int) -> bytes:
    feats = _build_features(DEFAULT_CONFIG, z, x, y)
    return sqlite3.Binary(encode_mvt(feats))


def _cm93_mvt_label_py(z: int, x: int, y: int) -> bytes:
    feats = [f for f in _build_features(DEFAULT_CONFIG, z, x, y) if "text" in f.get("properties", {})]
    return sqlite3.Binary(encode_mvt(feats))


_db.create_function("cm93_mvt_core", 3, _cm93_mvt_core_py)
_db.create_function("cm93_mvt_label", 3, _cm93_mvt_label_py)


def _query_mvt(func: str, z: int, x: int, y: int) -> bytes:
    row = _db.execute(f"SELECT {func}(?, ?, ?)", (z, x, y)).fetchone()
    return bytes(row[0]) if row and row[0] is not None else b""


@lru_cache(maxsize=512)
def _render_png(cfg: ContourConfig, z: int, x: int, y: int) -> bytes:  # pragma: no cover - trivial
    _ = (cfg, z, x, y)
    return PNG_1X1


@lru_cache(maxsize=256)
def _render_png_mvp(cfg: ContourConfig, z: int, x: int, y: int) -> bytes:
    if not render_raster:
        raise RasterMVPUnavailable("Pillow missing")
    bbox = _tile_bbox(z, x, y)
    classifier = _get_classifier(cfg)
    feats = []
    contours = []
    for feat in features_for_tile(bbox, z, x, y):
        props = dict(feat.get("properties", {}))
        objl = props.get("OBJL", "")
        props.update(classifier.classify(objl, props))
        feat_dict = {"geometry": feat["geometry"], "properties": props}
        feats.append(feat_dict)
        if objl == "DEPCNT":
            contours.append(feat_dict)
    mark = S52PreClassifier.finalize_tile(contours, cfg)
    for idx in mark:
        props = contours[idx]["properties"]
        props["role"] = "safety"
        props["isSafety"] = True
    return render_raster(z, x, y, feats, _day_colors)


@lru_cache(maxsize=512)
def _render_enc_mvt(ds: str, cfg: ContourConfig, z: int, x: int, y: int) -> bytes:
    """Render an ENC tile by querying features and encoding to MVT."""

    bbox = _tile_bbox(z, x, y)
    scale = 2 ** z
    raw_feats = query_features(ds, bbox, scale)
    classifier = _get_classifier(cfg)
    feats: List[Dict[str, Any]] = []
    contours: List[Dict[str, Any]] = []
    for feat in raw_feats:
        props = dict(feat.get("properties", {}))
        objl = props.get("OBJL", "")
        if not apply_scamin(objl, z):
            continue
        props.update(classifier.classify(objl, props))
        props["OBJL"] = _OBJL_CODES.get(objl, 0)
        feat_dict = {"geometry": feat["geometry"], "properties": props}
        feats.append(feat_dict)
        if objl == "DEPCNT":
            contours.append(feat_dict)
    mark = S52PreClassifier.finalize_tile(contours, cfg)
    for idx in mark:
        props = contours[idx]["properties"]
        props["role"] = "safety"
        props["isSafety"] = True
    return encode_mvt(feats)


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
def tiles_png(
    z: int,
    x: int,
    y: str,
    sc: float | None = None,
    safety: float | None = None,
    shallow: float | None = None,
    deep: float | None = None,
) -> Response:
    """Serve raster PNG tiles."""

    try:
        y_int = int(y)
    except ValueError:
        return JSONResponse({"error": "invalid tile"}, status_code=422)
    return tiles(
        z,
        x,
        y_int,
        fmt="png",
        sc=sc,
        safety=safety,
        shallow=shallow,
        deep=deep,
    )


@app.get("/tiles/cm93/{z}/{x}/{y}")
def tiles(
    z: int,
    x: int,
    y: int,
    fmt: str = "mvt",
    sc: float | None = None,
    safety: float | None = None,
    shallow: float | None = None,
    deep: float | None = None,
) -> Response:
    start = time.perf_counter()
    cfg = _cfg_from_params(sc, safety, shallow, deep)
    key = _cache_key(fmt, cfg, z, x, y, "")
    cached = _get_from_redis(key)
    if cached is not None:
        data = cached
        cache_state = "hit"
        media_type = "image/png" if fmt == "png" else "application/x-protobuf"
    else:
        cache_state = "miss"
        if fmt == "png-mvp" or (fmt == "png" and os.environ.get("RASTER_MVP") == "1"):
            before = _render_png_mvp.cache_info().hits
            try:
                data = _render_png_mvp(cfg, z, x, y)
            except RasterMVPUnavailable:
                data = PNG_1X1
            after = _render_png_mvp.cache_info().hits
            media_type = "image/png"
        elif fmt == "png":
            before = _render_png.cache_info().hits
            data = _render_png(cfg, z, x, y)
            after = _render_png.cache_info().hits
            media_type = "image/png"
        else:
            before = _render_mvt.cache_info().hits
            data = _render_mvt(cfg, z, x, y)
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
        cfg.safety,
        z,
        x,
        y,
        cache_state,
        duration_ms,
    )
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "X-Tile-Cache": cache_state,
        "Cache-Control": "public, max-age=60",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(content=data, media_type=media_type, headers=headers)


# ---------------------------------------------------------------------------
# ENC endpoint via OpenCPN bridge
# ---------------------------------------------------------------------------


@app.get("/tiles/enc/{ds}/{z}/{x}/{y}")
def tiles_enc_dataset(
    ds: str,
    z: int,
    x: int,
    y: int,
    fmt: str = "mvt",
    sc: float | None = None,
    safety: float | None = None,
    shallow: float | None = None,
    deep: float | None = None,
) -> Response:
    dataset = get_dataset(ds)
    if not dataset:
        return JSONResponse({"error": "dataset not found"}, status_code=404)
    if fmt != "mvt":
        return JSONResponse({"error": "unsupported format", "supported": ["mvt"]}, status_code=415)
    if z < 0 or x < 0 or y < 0 or x >= 2**z or y >= 2**z:
        return JSONResponse({"error": "invalid tile"}, status_code=422)
    cfg = _cfg_from_params(sc, safety, shallow, deep)
    key = _cache_key(fmt, cfg, z, x, y, ds)
    start = time.perf_counter()
    cached = _get_from_redis(key)
    cache_state = "hit" if cached is not None else "miss"
    if cached is not None:
        data = cached
    else:
        before = _render_enc_mvt.cache_info().hits
        data = _render_enc_mvt(ds, cfg, z, x, y)
        after = _render_enc_mvt.cache_info().hits
        if after > before:
            cache_state = "hit"
            _cache_hits.inc()
        _set_redis(key, data)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "fmt=%s ds=%s z=%d x=%d y=%d cache=%s ms=%.2f",
        fmt,
        ds,
        z,
        x,
        y,
        cache_state,
        duration_ms,
    )
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "X-Tile-Cache": cache_state,
        "Cache-Control": "public, max-age=60",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(content=data, media_type="application/x-protobuf", headers=headers)


@app.get("/tiles/enc/{z}/{x}/{y}")
def tiles_enc(
    z: int,
    x: int,
    y: int,
    fmt: str = "mvt",
    sc: float | None = None,
    safety: float | None = None,
    shallow: float | None = None,
    deep: float | None = None,
) -> Response:
    datasets = list_datasets()
    if len(datasets) == 1:
        return tiles_enc_dataset(
            datasets[0].id,
            z,
            x,
            y,
            fmt=fmt,
            sc=sc,
            safety=safety,
            shallow=shallow,
            deep=deep,
        )
    return JSONResponse(
        {
            "error": "dataset required",
            "available": [d.id for d in datasets],
        },
        status_code=404,
    )


@app.get("/config/contours")
def get_contours_config() -> Dict[str, float | None]:
    from dataclasses import asdict

    return asdict(DEFAULT_CONFIG)


@app.get("/config/datasource")
def get_datasource_config() -> Dict[str, object]:
    datasets = list_datasets()
    if datasets:
        return {
            "type": "enc",
            "datasets": [{"id": d.id, "path": str(d.path)} for d in datasets],
        }
    return {"type": "stub"}


@app.get("/style/s52.day.json")
def style() -> Response:
    path = STYLING_DIST / "style.s52.day.json"
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)


@app.get("/style/s52.dusk.json")
def style_dusk() -> Response:
    path = STYLING_DIST / "style.s52.dusk.json"
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)


@app.get("/style/s52.night.json")
def style_night() -> Response:
    path = STYLING_DIST / "style.s52.night.json"
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)


@app.get("/sprites/s52-day.json")
def sprite_json() -> Response:
    path = STYLING_DIST / "sprites" / "s52-day.json"
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)


@app.get("/sprites/s52-day.png")
def sprite_png() -> Response:
    path = STYLING_DIST / "assets" / "s52" / "rastersymbols-day.png"
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="image/png", headers=headers)


@app.get("/glyphs/{fontstack}/{rng}.pbf")
def glyph_pbf(fontstack: str, rng: str) -> Response:
    path = STYLING_DIST / "glyphs" / f"{rng}.pbf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="glyph range not found")
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/x-protobuf", headers=headers)


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(_prom_registry), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz() -> Response:
    return Response("OK")

# ---------------------------------------------------------------------------
# Chart registry API and GeoTIFF tile service
reg = get_registry()

@app.on_event("startup")
def _scan_registry() -> None:
    data_dir = Path(__file__).resolve().parent / "data"
    reg.scan([data_dir])


def _serialize(rec: ChartRecord) -> Dict[str, Any]:
    return {
        "id": rec.id,
        "kind": rec.kind,
        "name": rec.name,
        "bbox": rec.bbox,
        "minzoom": rec.minzoom,
        "maxzoom": rec.maxzoom,
        "updatedAt": rec.updatedAt,
        "path": rec.path,
        "url": rec.url,
        "tags": rec.tags or [],
    }


@app.get("/charts")
def charts_summary() -> Dict[str, Any]:
    datasets = [
        {
            "id": d.id,
            "title": d.title,
            "bounds": d.bounds,
            "minzoom": d.minzoom,
            "maxzoom": d.maxzoom,
        }
        for d in list_datasets()
    ]
    return {"base": ["osm", "geotiff", "enc"], "enc": {"datasets": datasets}}


@app.get("/charts/{cid}")
def chart_detail(cid: str) -> Dict[str, Any]:
    rec = reg.get(cid)
    if not rec:
        raise HTTPException(status_code=404, detail="chart not found")
    return _serialize(rec)


@app.get("/charts/{cid}/thumbnail")
def chart_thumbnail(cid: str):  # pragma: no cover - simple placeholder
    rec = reg.get(cid)
    if not rec:
        raise HTTPException(status_code=404, detail="chart not found")
    thumb = Path(str(rec.path) + ".png") if rec.path else None
    if thumb and thumb.exists():
        return Response(thumb.read_bytes(), media_type="image/png")
    raise HTTPException(status_code=404, detail="thumbnail not found")


@app.post("/charts/scan")
def charts_scan() -> Dict[str, Any]:
    data_dir = Path(__file__).resolve().parent / "data"
    reg.scan([data_dir])
    return {"scanned": True, "count": len(reg.list())}


if os.environ.get("IMPORT_API_ENABLED") == "1":
    class _EncReq(BaseModel):
        src: str
        respectScamin: bool | None = None
        name: str | None = None

    @app.post("/admin/import/enc", status_code=202)
    async def admin_import_enc(req: _EncReq) -> Dict[str, Any]:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve().parent / "tools" / "import_enc.py"),
            "--src",
            req.src,
        ]
        if req.name:
            cmd += ["--name", req.name]
        if req.respectScamin:
            cmd.append("--respect-scamin")
        proc = await asyncio.create_subprocess_exec(*cmd)
        return {"task": proc.pid}

    class _Cm93Req(BaseModel):
        src: str

    @app.post("/admin/import/cm93", status_code=202)
    async def admin_import_cm93(req: _Cm93Req) -> Dict[str, Any]:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve().parent / "tools" / "import_cm93.py"),
            "--src",
            req.src,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd)
        return {"task": proc.pid}

    class _GeoReq(BaseModel):
        src: str

    @app.post("/admin/import/geotiff", status_code=202)
    async def admin_import_geotiff(req: _GeoReq) -> Dict[str, Any]:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve().parent / "tools" / "import_geotiff.py"),
            "--src",
            req.src,
        ]
        proc = await asyncio.create_subprocess_exec(*cmd)
        return {"task": proc.pid}


# --- GeoTIFF tiles via pseudo MapProxy -------------------------------------
_GEO_CACHE_SIZE = int(os.environ.get("GEO_LRU_SIZE", "256"))
_geo_cache: "OrderedDict[str, bytes]" = globals().setdefault("_geo_cache", OrderedDict())
if "_geo_hits" not in globals():
    _geo_hits = Counter("geotiff_cache_hits", "GeoTIFF tile cache hits", registry=_prom_registry)
if "_geo_errors" not in globals():
    _geo_errors = Counter("geotiff_errors", "GeoTIFF tile render errors", registry=_prom_registry)


def _render_geotiff(cid: str, z: int, x: int, y: int, fmt: str) -> bytes:
    rec = reg.get(cid)
    if not rec or not rec.path:
        raise RuntimeError("chart not found")
    if Reader is None:
        return PNG_1X1
    with Reader(rec.path) as r:
        img, _ = r.tile(x, y, z)
    img_format = "WEBP" if fmt == "webp" else "PNG"
    return img.render(img_format=img_format)


@app.get("/titiler/tiles/{cid}/{z}/{x}/{y}.{fmt}")
def titiler_tiles(cid: str, z: int, x: int, y: int, fmt: str = "png") -> Response:
    fmt = fmt.lower()
    if fmt == "webp" and os.environ.get("GEO_WEBP") != "1":
        raise HTTPException(status_code=415, detail="unsupported format")
    data = _render_geotiff(cid, z, x, y, fmt)
    media = "image/webp" if fmt == "webp" else "image/png"
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "Cache-Control": "public, max-age=60",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type=media, headers=headers)


@app.get("/tiles/geotiff/{cid}/{z}/{x}/{y}.{fmt}")
def tiles_geotiff(cid: str, z: int, x: int, y: int, fmt: str = "png") -> Response:
    fmt = fmt.lower()
    if fmt == "webp" and os.environ.get("GEO_WEBP") != "1":
        raise HTTPException(status_code=415, detail="unsupported format")
    media = "image/webp" if fmt == "webp" else "image/png"
    key = f"{cid}:{z}/{x}/{y}.{fmt}"
    cached = _geo_cache.get(key)
    if cached is not None:
        _geo_cache.move_to_end(key)
        _geo_hits.inc()
        data = cached
        cache_state = "hit"
    else:
        try:
            data = _render_geotiff(cid, z, x, y, fmt)
            cache_state = "miss"
            _geo_cache[key] = data
            _geo_cache.move_to_end(key)
            if len(_geo_cache) > _GEO_CACHE_SIZE:
                _geo_cache.popitem(last=False)
        except Exception:
            _geo_errors.inc()
            cached = _geo_cache.get(key)
            if cached is None:
                raise HTTPException(status_code=502, detail="render error")
            data = cached
            cache_state = "stale"
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "X-Tile-Cache": cache_state,
        "Cache-Control": "public, max-age=60",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type=media, headers=headers)


# --- CM93 vector tiles ------------------------------------------------------


@app.get("/tiles/cm93-core/{z}/{x}/{y}.pbf")
def tiles_cm93_core(z: int, x: int, y: int) -> Response:
    data = _query_mvt("cm93_mvt_core", z, x, y)
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "Cache-Control": "public, max-age=60",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/x-protobuf", headers=headers)


@app.get("/tiles/cm93-label/{z}/{x}/{y}.pbf")
def tiles_cm93_label(z: int, x: int, y: int) -> Response:
    data = _query_mvt("cm93_mvt_label", z, x, y)
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "Cache-Control": "public, max-age=60",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/x-protobuf", headers=headers)


@app.get("/tiles/cm93/dict.json")
def tiles_cm93_dict() -> Response:
    path = STYLING_DIST / "dict.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="dict missing")
    data = path.read_bytes()
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "Cache-Control": "public, max-age=3600",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)


@app.get("/tiles/cm93-core.tilejson")
def tiles_cm93_core_tilejson() -> Response:
    data = json.dumps(
        {
            "tilejson": "3.0.0",
            "tiles": ["/tiles/cm93-core/{z}/{x}/{y}.pbf"],
            "minzoom": 0,
            "maxzoom": 16,
            "bounds": [-180.0, -85.0511, 180.0, 85.0511],
            "attribution": "© OpenCPN",
            "vector_layers": [{"id": "features"}],
        }
    ).encode("utf-8")
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "Cache-Control": "public, max-age=3600",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)


@app.get("/tiles/cm93-label.tilejson")
def tiles_cm93_label_tilejson() -> Response:
    data = json.dumps(
        {
            "tilejson": "3.0.0",
            "tiles": ["/tiles/cm93-label/{z}/{x}/{y}.pbf"],
            "minzoom": 0,
            "maxzoom": 16,
            "bounds": [-180.0, -85.0511, 180.0, 85.0511],
            "attribution": "© OpenCPN",
            "vector_layers": [{"id": "features"}],
        }
    ).encode("utf-8")
    etag = hashlib.sha1(data).hexdigest()
    headers = {
        "Cache-Control": "public, max-age=3600",
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    return Response(data, media_type="application/json", headers=headers)
