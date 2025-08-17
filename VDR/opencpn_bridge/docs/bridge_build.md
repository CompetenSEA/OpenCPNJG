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
