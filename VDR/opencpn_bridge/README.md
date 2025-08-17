# OpenCPN Bridge

This directory contains a small experimental bridge exposing parts of the
[OpenCPN](https://opencpn.org) chart processing stack to Python.  The current
implementation is a pure Python stub that records chart provenance and
returns empty feature data.

## Source layout

| Path | Origin | Notes |
| ---- | ------ | ----- |
| `py/bridge.py` | This repository | Python stub implementing the public API. |
| `CMakeLists.txt`, `pyproject.toml` | This repository | Build and packaging glue. |
| `s57chart.cpp`, `Osenc.cpp`, `cm93.cpp`, `s52plib/` | Copied verbatim from the OpenCPN project | Currently **unused** in the build. They are kept as references for future integration and still carry the GPLv2+ license from OpenCPN. |

The copied OpenCPN files are not part of the stub because they depend on
large portions of the upstream application (wxWidgets, GDAL, PROJ, etc.).

### Syncing with upstream

When OpenCPN is updated, refresh the copies manually:

1. Download a matching OpenCPN release or commit.
2. Replace the files listed above with their new versions.
3. Resolve any new includes or dependencies by either porting the required
   code into `opencpn_bridge/` or stubbing it out.  Avoid scripting or
   automatic downloads so that changes can be reviewed carefully.

## Building

The Python stub requires no compilation.  To build the optional C++
extension based on the ocpn-mini sources, configure CMake with
`-DOPB_STUB_ONLY=OFF -DOPB_WITH_OCPN_MINI=ON`.

```bash
cmake -S . -B build
cmake --build build
```

The compiled extension module will be placed in `dist/`.

## Python usage

```python
from opencpn_bridge import build_senc, query_tile_mvt

handle = build_senc("/path/to/dataset", "/tmp/out")
tile = query_tile_mvt(handle, 0, 0, 0, 0, 0, 0, 0)
print(tile)
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
   `query_tile_mvt` instead of returning placeholders.
4. **Automated tests** – add Python and C++ unit tests exercising handle
   lifetime and basic query behaviour.
5. **Wheel builds** – extend the packaging configuration to emit wheels for
   common platforms using `scikit-build-core`.
