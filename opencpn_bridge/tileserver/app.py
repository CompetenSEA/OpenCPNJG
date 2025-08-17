"""Minimal FastAPI tileserver backed by opencpn_bridge."""

from __future__ import annotations

import importlib
import time

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Lazily import the native bridge module to access query_tile_mvt
_bridge = importlib.import_module("opencpn_bridge")
query_tile_mvt = getattr(_bridge, "query_tile_mvt", None)

app = FastAPI()

# Prometheus metrics placeholders
_tiles_requested = Counter(
    "tiles_requested_total", "Total tile requests", ["kind"],
)
_tile_seconds = Histogram(
    "tile_render_seconds", "Tile render time", ["kind"],
)


def _build_response(kind: str, tile_id: str, z: int, x: int, y: int) -> Response:
    if query_tile_mvt is None:  # pragma: no cover - native dependency missing
        raise HTTPException(status_code=500, detail="query_tile_mvt unavailable")

    start = time.perf_counter()
    data, tile_hash, compressed = query_tile_mvt(kind, tile_id, z, x, y)
    _tile_seconds.labels(kind=kind).observe(time.perf_counter() - start)
    _tiles_requested.labels(kind=kind).inc()

    headers = {
        "Content-Type": "application/x-protobuf",
        "Cache-Control": "public,max-age=3600",
        "ETag": tile_hash,
    }
    if compressed:
        headers["Content-Encoding"] = "gzip"
    return Response(content=data, media_type="application/x-protobuf", headers=headers)


@app.get("/tiles/enc/{chart_id}/{z}/{x}/{y}.pbf")
async def enc_tile(chart_id: str, z: int, x: int, y: int) -> Response:
    """Return ENC tile MVT."""
    return _build_response("enc", chart_id, z, x, y)


@app.get("/tiles/cm93/{chart_id}/{z}/{x}/{y}.pbf")
async def cm93_tile(chart_id: str, z: int, x: int, y: int) -> Response:
    """Return CM93 tile MVT."""
    return _build_response("cm93", chart_id, z, x, y)


@app.get("/healthz")
async def healthz() -> dict:
    """Simple health check endpoint."""
    return {"ok": True}


@app.get("/charts")
async def charts() -> dict:
    """Placeholder charts listing."""
    return {"charts": []}


@app.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
