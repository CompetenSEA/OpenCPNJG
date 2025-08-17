# OpenCPN Bridge

This module exposes a tiny slice of the OpenCPN chart stack to Python.  It is
used to experiment with SENC generation and feature queries without the full
application.

## Build

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

The build emits a Python extension and a small CLI.

## End-to-End Usage

The CLI at `cli/opb.py` stages chart assets, ingests datasets, and runs a
development tileserver.

```bash
# Stage S-52 symbol resources
python cli/opb.py stage-s52

# Build a SENC from a chart directory and register it
python cli/opb.py ingest demo /charts/demo -t enc

# Start the FastAPI tileserver
python cli/opb.py serve --host 127.0.0.1 --port 8000

# Fetch a tile
curl http://127.0.0.1:8000/tiles/0/0/0.png -o tile.png
```

The server uses the standard XYZ tile scheme and returns 256×256 PNG tiles.

Example Python session:

```python
from opencpn_bridge import build_senc, query_features

handle = build_senc("/charts/demo.000")
feats = query_features(handle, (-180, -90, 180, 90), 25000)
print(feats)
```

Release builds are pushed to the container registry and deployed alongside the
production tileserver.
