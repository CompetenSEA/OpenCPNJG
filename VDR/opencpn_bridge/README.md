# OpenCPN Bridge

This directory contains a small experimental bridge exposing parts of the
[OpenCPN](https://opencpn.org) chart processing stack to Python.
It packages a minimal C++ library together with `pybind11` wrappers
so that Python code can build S57 SENC caches and query chart features.

The implementation here is intentionally minimal – the heavy lifting
performed by OpenCPN is **not** reproduced.  The functions simply store
chart paths and return empty feature sets, acting as a scaffold for future
work.

## Source layout

| Path | Origin | Notes |
| ---- | ------ | ----- |
| `bridge.cpp`, `bridge.h`, `pybind.cpp` | This repository | C++ handle registry and the Python bindings. |
| `CMakeLists.txt`, `pyproject.toml` | This repository | Build and packaging glue. |
| `s57chart.cpp`, `Osenc.cpp`, `cm93.cpp`, `s52plib/` | Copied verbatim from the OpenCPN project | Currently **unused** in the build. They are kept as references for future integration and still carry the GPLv2+ license from OpenCPN. |

Only the wrapper sources are compiled today; the copied OpenCPN files are
not part of the build because they depend on large portions of the
upstream application (wxWidgets, GDAL, PROJ, etc.).

### Syncing with upstream

When OpenCPN is updated, refresh the copies manually:

1. Download a matching OpenCPN release or commit.
2. Replace the files listed above with their new versions.
3. Resolve any new includes or dependencies by either porting the required
   code into `opencpn_bridge/` or stubbing it out.  Avoid scripting or
   automatic downloads so that changes can be reviewed carefully.

## Building

```bash
cmake -S . -B build
cmake --build build
```

The compiled extension module will be placed in `dist/`.

No external libraries beyond a C++17 compiler and Python are required for
this stub implementation.  Integrating the full OpenCPN sources would
add dependencies on wxWidgets, GDAL, and other libraries that are not yet
provided here.

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

## Coding tasks

These items track future work needed to turn the stub into a functional
bridge:

1. **Port core OpenCPN classes** – introduce minimal stubs for the
   wxWidgets and GDAL types so that `s57chart.cpp`, `Osenc.cpp`, and
   `cm93.cpp` can be compiled.
2. **Implement SENC generation** – hook `build_senc` up to the S‑57 and
   CM93 readers once the above compiles.
3. **Expose feature data** – populate real feature objects in
   `query_features` instead of returning placeholders.
4. **Automated tests** – add Python and C++ unit tests exercising handle
   lifetime and basic query behaviour.
5. **Wheel builds** – extend the packaging configuration to emit wheels for
   common platforms using `scikit-build-core`.
