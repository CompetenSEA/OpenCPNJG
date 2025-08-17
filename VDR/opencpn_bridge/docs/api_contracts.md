# API Contracts

The bridge exposes a minimal set of native functions and a small HTTP
service for development.

## Python bindings

```python
def build_senc(path: str) -> str:
    """Create a SENC and return a handle used by the tileserver."""


def query_features(handle: str, bbox: tuple[float, float, float, float], scale: float) -> dict:
    """Return features intersecting the bounding box."""
```

## HTTP endpoints

- `GET /tiles/{z}/{x}/{y}.png` – return a 256×256 PNG tile using the
  standard XYZ scheme (Web Mercator, origin top‑left).
- `GET /metrics` – Prometheus metrics for tile renders and byte counts.

The CLI wraps the bindings and defaults to local staging services.  Once
tiles look correct they can be pushed to the registry and served from
production.
