# OpenCPN Bridge

This directory provides a small bridge exposing parts of the
[OpenCPN](https://opencpn.org) chart-processing stack to Python.  At
import-time it attempts to load a compiled extension and automatically falls
back to lightweight Python stubs when the extension is unavailable.  The stubs
record dataset provenance and emit empty but valid tiles so applications can be
developed without native dependencies.

## Dynamic loading

``opencpn_bridge.py.bridge`` prefers the native
``opencpn_bridge.opencpn_bridge`` module.  If it cannot be imported the module
substitutes a pure Python implementation with the same API.  All implementations
return a ``(data, etag, compressed)`` tuple from ``query_tile_mvt``.

## Python usage

```python
from opencpn_bridge.py.bridge import build_senc, query_tile_mvt

handle = build_senc("/path/to/dataset", "/tmp/out")
data, etag, compressed = query_tile_mvt(handle, 0, 0, 0)
```

## Command line interface

The ``opb`` command exposes bridge utilities:

* ``opb stage-s52`` – copy S‑52 symbol assets into ``dist/assets/s52/``.
* ``opb ingest <dataset_id> <src_root> --type enc|cm93`` – build a SENC and
  record it in the registry.
* ``opb serve [--host 0.0.0.0] [--port 8000]`` – run the FastAPI tile server.

## Registry and staged assets

Chart metadata is stored in a SQLite registry located at
``registry/registry.sqlite``.  This file is not committed to version control; a
placeholder ``registry.sqlite.txt`` is provided.

S‑52 assets staged by ``opb stage-s52`` are written to ``dist/assets/s52/`` with
an accompanying ``assets.manifest.json``.  These assets are required by the
tile server when rendering ENC tiles.
