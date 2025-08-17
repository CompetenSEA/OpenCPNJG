from __future__ import annotations

"""Prometheus metrics for tile rendering."""

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

REGISTRY = CollectorRegistry()

# Histogram tracking tile rendering latency by endpoint kind
# (e.g. cm93-core, cm93-label, geotiff).
tile_render_seconds = Histogram(
    "tile_render_seconds",
    "Latency for tile rendering in seconds",
    ["kind"],
    registry=REGISTRY,
)

# Counter recording total bytes returned per endpoint kind.
tile_bytes_total = Counter(
    "tile_bytes_total",
    "Total bytes returned for tiles",
    ["kind"],
    registry=REGISTRY,
)

# Gauge recording size in bytes of the most recent tile response per endpoint kind.
tile_size_bytes = Gauge(
    "tile_size_bytes",
    "Size of the last tile rendered in bytes",
    ["kind"],
    registry=REGISTRY,
)

# Gauge tracking resident memory usage of the tile server process.
process_resident_memory_bytes = Gauge(
    "process_resident_memory_bytes",
    "Resident memory used by the tile server in bytes",
    registry=REGISTRY,
)

__all__ = [
    "REGISTRY",
    "tile_render_seconds",
    "tile_bytes_total",
    "tile_size_bytes",
    "process_resident_memory_bytes",
    "CONTENT_TYPE_LATEST",
    "generate_latest",
]
