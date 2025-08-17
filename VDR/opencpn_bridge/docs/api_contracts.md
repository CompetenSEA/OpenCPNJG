# API Contracts


The bridge exposes a minimal set of native functions and a small HTTP
service for development.

## Python bindings
The bridge aims to serve tiles over HTTP and through a small CLI.  Stub
functions provide the core operations:
The Python package exposes these entry points:

```python
from opencpn_bridge import build_senc, query_tile_mvt
```


```python
def build_senc(path: str) -> str:
    """Create a SENC and return a handle used by the tileserver."""


def query_features(handle: str, bbox: tuple[float, float, float, float], scale: float) -> dict:
    """Return features intersecting the bounding box."""
```

Helper utilities for bounding boxes:

```python
def xyz_to_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    """Return (west, south, east, north) for a tile in degrees."""

def bbox_to_xyz(z: int, west: float, south: float, east: float, north: float) -> tuple[int, int]:
    """Inverse of xyz_to_bbox for tile-aligned bounding boxes."""
```


Proposed tile endpoints:

- `GET /tiles/{z}/{x}/{y}.png` – return a 256×256 PNG tile using the
  standard XYZ scheme (Web Mercator, origin top‑left).
- `GET /metrics` – Prometheus metrics for tile renders and byte counts.

The CLI wraps the bindings and defaults to local staging services.  Once
tiles look correct they can be pushed to the registry and served from
production.
