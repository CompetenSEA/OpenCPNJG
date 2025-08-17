"""Minimal FastAPI tileserver backed by ``query_tile_mvt``.

Exposes endpoints for health checks, Prometheus metrics and vector tiles for
ENC and CM93 chart datasets.  Tile responses include appropriate caching
headers and optional gzip compression if the underlying data has been
pre-compressed.
"""

from __future__ import annotations

import importlib
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Response

from .metrics import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    generate_latest,
    tile_bytes_total,
    tile_render_seconds,
)

# Lazily import the native bridge module to access ``query_tile_mvt``
try:  # pragma: no cover - optional native dependency
    _bridge = importlib.import_module("opencpn_bridge")
    query_tile_mvt = getattr(_bridge, "query_tile_mvt", None)
except Exception:  # pragma: no cover - dependency missing
    query_tile_mvt = None

# ``list_datasets`` lives in the chart registry package which may not be
# available in all environments (e.g. unit tests), so import lazily.
try:  # pragma: no cover - optional dependency
    from ..registry import list_datasets as _list_datasets
except Exception:  # pragma: no cover - optional dependency missing
    _list_datasets = None

app = FastAPI()


def _build_tile_response(kind: str, chart_id: str, z: int, x: int, y: int) -> Response:
    """Render a tile and wrap it in an HTTP response."""

    if query_tile_mvt is None:  # pragma: no cover - native dependency missing
        raise HTTPException(status_code=500, detail="query_tile_mvt unavailable")

    start = time.perf_counter()
    data, tile_hash, compressed = query_tile_mvt(kind, chart_id, z, x, y)
    tile_render_seconds.labels(kind=kind).observe(time.perf_counter() - start)
    tile_bytes_total.labels(kind=kind).inc(len(data))

    headers = {
        "Cache-Control": "public,max-age=3600",
    }
    if tile_hash:
        headers["ETag"] = tile_hash
    if compressed:
        headers["Content-Encoding"] = "gzip"

    return Response(
        content=data,
        media_type="application/x-protobuf",
        headers=headers,
    )


@app.get("/tiles/enc/{chart_id}/{z}/{x}/{y}.pbf")
def enc_tile(chart_id: str, z: int, x: int, y: int) -> Response:
    """Return ENC tile as Mapbox Vector Tile."""

    return _build_tile_response("enc", chart_id, z, x, y)


@app.get("/tiles/cm93/{chart_id}/{z}/{x}/{y}.pbf")
def cm93_tile(chart_id: str, z: int, x: int, y: int) -> Response:
    """Return CM93 tile as Mapbox Vector Tile."""

    return _build_tile_response("cm93", chart_id, z, x, y)


@app.get("/charts")
def charts() -> dict[str, Any]:
    """List datasets known to the registry."""

    datasets: list[dict[str, Any]] = []
    if _list_datasets is not None:  # pragma: no branch - depends on optional import
        try:
            for d in _list_datasets():
                datasets.append(
                    {
                        "id": d.id,
                        "title": d.title,
                        "bounds": d.bounds,
                        "minzoom": d.minzoom,
                        "maxzoom": d.maxzoom,
                    }
                )
        except Exception:  # pragma: no cover - registry failure
            datasets = []
    return {"base": ["osm", "geotiff", "enc"], "enc": {"datasets": datasets}}


@app.get("/healthz")
def healthz() -> dict[str, bool]:
    """Kubernetes-style liveness probe."""

    return {"ok": True}


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""

    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
