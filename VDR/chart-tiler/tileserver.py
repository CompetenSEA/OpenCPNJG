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
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
import hashlib
from registry import get_registry, ChartRecord, list_datasets, get_dataset
from typing import Dict, Optional, List, Any

try:
    from rio_tiler.io import Reader  # type: ignore
except Exception:  # pragma: no cover
    Reader = None

from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    CollectorRegistry,
    generate_latest,
)

try:  # pragma: no cover - redis optional
    import redis
except Exception:  # pragma: no cover
    redis = None

from datasource_stub import features_for_tile
from mvt_builder import encode_mvt
from s52_preclass import S52PreClassifier, ContourConfig
try:  # pragma: no cover - optional pillow
    from raster_mvp import render_tile as render_raster, RasterMVPUnavailable
except Exception:  # pragma: no cover
    render_raster = None  # type: ignore
    class RasterMVPUnavailable(Exception):
        pass
try:
    from datasource_mbtiles import MBTilesDataSource, get_datasource  # type: ignore
except Exception:  # pragma: no cover - optional
    MBTilesDataSource = None  # type: ignore
    def get_datasource(path: str):  # type: ignore
        raise RuntimeError("MBTiles support unavailable")

# Allow importing parsing helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server-styling"))
from s52_xml import parse_day_colors, parse_symbols


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
logger = logging.getLogger("tileserver")

_prom_registry = globals().setdefault("_prom_registry", CollectorRegistry())
_tile_gen_ms = globals().setdefault(
    "_tile_gen_ms",
    Histogram("tile_gen_ms", "Time spent generating tiles", unit="ms", registry=_prom_registry),
)
_cache_hits = globals().setdefault(
    "_cache_hits", Counter("cache_hits", "Cache hits", registry=_prom_registry)
)
_redis: Optional["redis.Redis"] = (
    redis.from_url(os.environ["REDIS_URL"]) if redis and "REDIS_URL" in os.environ else None
)
_redis_ttl = int(os.environ.get("REDIS_TTL", "0"))

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


@lru_cache(maxsize=32)
def _get_classifier(cfg: ContourConfig) -> S52PreClassifier:
    return S52PreClassifier(cfg, _day_colors, symbols=_symbols)


@lru_cache(maxsize=512)
def _render_mvt(cfg: ContourConfig, z: int, x: int, y: int) -> bytes:
    """Build a Mapbox Vector Tile for the requested tile."""

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

    with _tile_gen_ms.time():
        return encode_mvt(feats)


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


def _serve_mbtiles(
    mb: MBTilesDataSource,
    ds_id: str,
    z: int,
    x: int,
    y: int,
    fmt: str,
    cfg: ContourConfig,
) -> Response:
    if fmt != "mvt":
        return Response(status_code=415)
    key = _cache_key(fmt, cfg, z, x, y, ds_id)
    cached = _get_from_redis(key)
    cache_state = "hit" if cached is not None else "miss"
    if cached is not None:
        headers = {"X-Tile-Cache": cache_state, "Cache-Control": "public, max-age=60"}
        etag_src = f"{mb.path}:{z}:{x}:{y}".encode()
        headers["ETag"] = hashlib.sha1(etag_src).hexdigest()
        return Response(content=cached, media_type="application/x-protobuf", headers=headers)
    data = mb.get_tile(z, x, y)
    if data is None:
        return Response(status_code=204)
    _set_redis(key, data)
    headers = {"X-Tile-Cache": cache_state, "Cache-Control": "public, max-age=60"}
    etag_src = f"{mb.path}:{z}:{x}:{y}".encode()
    headers["ETag"] = hashlib.sha1(etag_src).hexdigest()
    return Response(content=data, media_type="application/x-protobuf", headers=headers)


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
        return Response(status_code=422)
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
    cache_state = "hit" if cached is not None else "miss"
    if cached is not None:
        media = "image/png" if fmt == "png" else "application/x-protobuf"
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
        headers = {"X-Tile-Cache": cache_state}
        if media.startswith("image/"):
            headers["Cache-Control"] = "public, max-age=60"
        return Response(content=cached, media_type=media, headers=headers)

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
    headers = {"X-Tile-Cache": cache_state}
    if media_type.startswith("image/"):
        headers["Cache-Control"] = "public, max-age=60"
    return Response(content=data, media_type=media_type, headers=headers)


# ---------------------------------------------------------------------------
# ENC endpoint (MBTiles backed)
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
        raise HTTPException(status_code=404)
    cfg = _cfg_from_params(sc, safety, shallow, deep)
    mb = get_datasource(str(dataset.path))
    start = time.perf_counter()
    resp = _serve_mbtiles(mb, ds, z, x, y, fmt, cfg)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "fmt=%s ds=%s z=%d x=%d y=%d cache=%s ms=%.2f",
        fmt,
        ds,
        z,
        x,
        y,
        resp.headers.get("X-Tile-Cache", "miss"),
        duration_ms,
    )
    return resp


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
    raise HTTPException(status_code=404)


@app.get("/config/contours")
def get_contours_config() -> Dict[str, float | None]:
    from dataclasses import asdict

    return asdict(DEFAULT_CONFIG)


@app.get("/config/datasource")
def get_datasource_config() -> Dict[str, object]:
    datasets = list_datasets()
    if datasets:
        return {
            "type": "mbtiles",
            "datasets": [
                {"id": d.id, "path": str(d.path), "summary": get_datasource(str(d.path)).summary()}
                for d in datasets
            ],
        }
    return {"type": "stub"}


@app.get("/style/s52.day.json")
def style() -> Response:
    path = STYLING_DIST / "style.s52.day.json"
    return Response(path.read_bytes(), media_type="application/json")


@app.get("/style/s52.dusk.json")
def style_dusk() -> Response:
    path = STYLING_DIST / "style.s52.dusk.json"
    return Response(path.read_bytes(), media_type="application/json")


@app.get("/style/s52.night.json")
def style_night() -> Response:
    path = STYLING_DIST / "style.s52.night.json"
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
        raise HTTPException(status_code=404)
    return _serialize(rec)


@app.get("/charts/{cid}/thumbnail")
def chart_thumbnail(cid: str):  # pragma: no cover - simple placeholder
    rec = reg.get(cid)
    if not rec:
        raise HTTPException(status_code=404)
    thumb = Path(str(rec.path) + ".png") if rec.path else None
    if thumb and thumb.exists():
        return Response(thumb.read_bytes(), media_type="image/png")
    raise HTTPException(status_code=404)


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
_geo_hits = globals().setdefault(
    "_geo_hits", Counter("geotiff_cache_hits", "GeoTIFF tile cache hits", registry=_prom_registry)
)
_geo_errors = globals().setdefault(
    "_geo_errors", Counter("geotiff_errors", "GeoTIFF tile render errors", registry=_prom_registry)
)


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
        raise HTTPException(status_code=415)
    data = _render_geotiff(cid, z, x, y, fmt)
    media = "image/webp" if fmt == "webp" else "image/png"
    return Response(data, media_type=media, headers={"Cache-Control": "public, max-age=60"})


@app.get("/tiles/geotiff/{cid}/{z}/{x}/{y}.{fmt}")
def tiles_geotiff(cid: str, z: int, x: int, y: int, fmt: str = "png") -> Response:
    fmt = fmt.lower()
    if fmt == "webp" and os.environ.get("GEO_WEBP") != "1":
        raise HTTPException(status_code=415)
    media = "image/webp" if fmt == "webp" else "image/png"
    key = f"{cid}:{z}/{x}/{y}.{fmt}"
    cached = _geo_cache.get(key)
    if cached is not None:
        _geo_cache.move_to_end(key)
        _geo_hits.inc()
        return Response(cached, media_type=media, headers={"X-Tile-Cache": "hit", "Cache-Control": "public, max-age=60"})
    try:
        data = _render_geotiff(cid, z, x, y, fmt)
    except Exception:
        _geo_errors.inc()
        cached = _geo_cache.get(key)
        if cached is not None:
            return Response(cached, media_type=media, headers={"X-Tile-Cache": "stale", "Cache-Control": "public, max-age=60"})
        raise HTTPException(status_code=502)
    _geo_cache[key] = data
    _geo_cache.move_to_end(key)
    if len(_geo_cache) > _GEO_CACHE_SIZE:
        _geo_cache.popitem(last=False)
    return Response(data, media_type=media, headers={"X-Tile-Cache": "miss", "Cache-Control": "public, max-age=60"})
