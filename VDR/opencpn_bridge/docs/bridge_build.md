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

## Dataset registry

Ingested datasets are tracked in a SQLite database located at `registry/registry.sqlite`.
The `ingest_dataset` helper populates a `datasets` table with:

- `id` – dataset identifier.
- `type` – dataset type.
- `bounds` – JSON encoded bounding box.
- `minzoom` and `maxzoom` – zoom levels derived from the dataset.
- `senc_path` – path to the generated SENC cache.
- `provenance_path` – path to the provenance metadata.

The database is created automatically when the first dataset is ingested.
A placeholder `registry.sqlite.txt` is provided in version control; rename or
replace it with `registry.sqlite` for local development.
