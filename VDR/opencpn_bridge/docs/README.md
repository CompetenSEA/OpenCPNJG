# OpenCPN Bridge

This module exposes a tiny slice of the OpenCPN chart stack to Python.  It is
used to experiment with SENC generation and vector tile queries without the
full application.

## Quickstart

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

The build emits a Python extension that can be driven from the CLI.  During
local testing point the CLI at the staging tileserver and registry:

```bash
./bridge_cli --registry https://registry.example/staging \
             --tileserver https://tiles.staging.example
```

Example Python session:

```python
from opencpn_bridge import build_senc, query_tile_mvt

handle = build_senc("/charts/demo.000")
tile = query_tile_mvt(handle, 0, 0, 0)
print(len(tile))
```

Release builds are pushed to the container registry and deployed alongside the
production tileserver.
