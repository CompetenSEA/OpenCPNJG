# Bridge Build

The bridge uses CMake and pybind11 to produce a small extension module.
Typical options:

- `-DCMAKE_BUILD_TYPE=Debug` – development builds for staging and CLI tests.
- `-DCMAKE_BUILD_TYPE=Release` – optimized builds published to the registry.
- `-DBUILD_SHARED_LIBS=ON` – emit a shared library instead of a module.

Example release build:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

After compiling, use the CLI against the staging tileserver to verify output
before pushing images to the registry.

## Staging S-52 Assets

Before building, stage the S-52/S-57 support files required at runtime:

```bash
python tools/stage_s52_assets.py
```

This copies the minimal symbol and metadata files from `data/s57data/` into
`dist/assets/s52/` and generates `assets.manifest.json` with SHA-256 hashes and
a `PROVENANCE.txt` recording the upstream repository and commit.
