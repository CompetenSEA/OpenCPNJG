# Bridge Build

The bridge uses CMake and pybind11 to produce a small extension module.

## Build options

- `-DCMAKE_BUILD_TYPE=Debug` – development builds for staging and CLI tests.
- `-DCMAKE_BUILD_TYPE=Release` – optimized builds published to the registry.
- `-DBUILD_SHARED_LIBS=ON` – emit a shared library instead of a module.
- `-DOPB_STUB_ONLY=ON` – compile only the stub bridge with no OpenCPN code.
- `-DOPB_WITH_OCPN_MINI=ON` – include vendored `ocpn-mini` sources; requires
  `OPB_STUB_ONLY` to be `OFF`.

Example stub build:

```bash
cmake -S . -B build -DOPB_STUB_ONLY=ON
cmake --build build
```

Example build with vendored sources:

```bash
cmake -S . -B build -DOPB_WITH_OCPN_MINI=ON -DOPB_STUB_ONLY=OFF
cmake --build build
```

## Runtime layout

The compiled module is written to `dist/opencpn_bridge.*`.
The CLI expects S-52 assets and SENC caches under
`chart-tiler/assets/senc` and uses the registry from `chart-tiler` to
look up datasets.  The `serve` command starts a FastAPI app that reads
these caches and serves tiles from `http://host:port/tiles/{z}/{x}/{y}.png`.

After compiling, use the CLI against the staging tileserver to verify output
before pushing images to the registry.
