from __future__ import annotations
"""Prometheus metrics for the lightweight tile server."""

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

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
