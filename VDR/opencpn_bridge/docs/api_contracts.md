# API Contracts

The bridge aims to serve tiles over HTTP and through a small CLI.  Stub
functions provide the core operations:
The Python package exposes these entry points:

```python
from opencpn_bridge import build_senc, query_tile_mvt
```


```python
def build_senc(path: str) -> str:
    """Create a SENC and return a handle used by the tileserver."""
    ...


def query_tile_mvt(handle: str, z: int, x: int, y: int) -> bytes:
    """Return an MVT tile for the given chart handle."""
    ...
```

Helper utilities for bounding boxes:

```python
def xyz_to_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    """Return (west, south, east, north) for a tile in degrees."""

def bbox_to_xyz(z: int, west: float, south: float, east: float, north: float) -> tuple[int, int]:
    """Inverse of xyz_to_bbox for tile-aligned bounding boxes."""
```


Proposed tile endpoints:

- `POST /v1/charts` – runs `build_senc` and stages the result in the registry.
- `GET /tiles/{handle}/{z}/{x}/{y}.mvt` – calls `query_tile_mvt`.

The CLI wraps these calls and defaults to the staging tileserver.  Once tiles
look correct they can be pushed to the registry and served from production.
