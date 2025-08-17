# API Contracts

The bridge aims to serve tiles over HTTP and through a small CLI.  Stub
functions provide the core operations:

```python
def build_senc(path: str) -> str:
    """Create a SENC and return a handle used by the tileserver."""
    ...


def query_tile_mvt(handle: str, z: int, x: int, y: int) -> bytes:
    """Return an MVT tile for the given chart handle."""
    ...
```

Proposed tile endpoints:

- `POST /v1/charts` – runs `build_senc` and stages the result in the registry.
- `GET /tiles/{handle}/{z}/{x}/{y}.mvt` – calls `query_tile_mvt`.

The CLI wraps these calls and defaults to the staging tileserver.  Once tiles
look correct they can be pushed to the registry and served from production.
