# OpenCPN Bridge

This directory contains a small experimental bridge exposing parts of the
[OpenCPN](https://opencpn.org) chart processing stack to Python.
It packages a minimal C++ library together with `pybind11` wrappers
so that Python code can build S57 SENC caches and query chart features.

The implementation here is intentionally minimal – the heavy lifting
performed by OpenCPN is **not** reproduced.  The functions simply store
chart paths and return empty feature sets, acting as a scaffold for future
work.

## Building

```bash
cmake -S . -B build
cmake --build build
```

The compiled extension module will be placed in `dist/`.

## Python usage

```python
from opencpn_bridge import build_senc, query_features

handle = build_senc("/path/to/chart.000")
features = query_features(handle, (0.0, 0.0, 1.0, 1.0), 20000.0)
print(features)
```

## Notes

* Handles returned by `build_senc` are kept for the lifetime of the
  process.  No explicit destruction API is provided.
* All functions are protected by a global mutex and are therefore
  thread‑safe at the expense of potential contention.
* The copied OpenCPN sources retain their original GPL licensing.
