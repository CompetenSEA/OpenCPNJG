from __future__ import annotations
"""Prometheus metrics for the lightweight tile server.

This module exposes two metrics shared by the FastAPI application:

``tile_render_seconds``
    Histogram tracking how long it takes to render a tile.

``tile_bytes_total``
    Counter recording the number of bytes returned to clients.
"""

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

# Separate registry so tests can introspect without polluting default metrics
REGISTRY = CollectorRegistry()

# Histogram tracking the render latency for tiles.
tile_render_seconds = Histogram(
    "tile_render_seconds",
    "Time spent rendering tiles in seconds",
    ["kind"],
    registry=REGISTRY,
)

# Counter recording total bytes returned for tiles.
tile_bytes_total = Counter(
    "tile_bytes_total",
    "Total number of bytes returned for tiles",
    ["kind"],
    registry=REGISTRY,
)

__all__ = [
    "REGISTRY",
    "tile_render_seconds",
    "tile_bytes_total",
    "CONTENT_TYPE_LATEST",
    "generate_latest",
]
