# OCPN Mini Vendor Bundle

The **ocpn-mini** build ships with a curated set of third-party libraries. This file documents which vendor code is included, the rules used to prune unnecessary files, and the provenance of each upstream project.

## Vendor File List
- `libs/rapidjson` – JSON parser for chart metadata.
- `libs/tinyxml` – lightweight XML reader for plugin manifests.
- `libs/sqlite` – embedded database backing settings storage.
- `libs/lz4` – compression routines for tile archives.
- `libs/pugixml` – fast DOM parser used in test helpers.

## Pruning Rules
- Include only headers and minimal sources required for runtime.
- Drop all vendor test suites, examples, and platform-specific code not needed by ocpn-mini.
- Remove documentation and tooling files that bloat the package.

## Upstream Provenance
- **rapidjson** sourced from <https://github.com/Tencent/rapidjson> (MIT) @ v1.1.0.
- **tinyxml** sourced from <https://github.com/leethomason/tinyxml2> (zlib) @ v9.0.0.
- **sqlite** sourced from <https://www.sqlite.org> (Public Domain) @ 3.45 series.
- **lz4** sourced from <https://github.com/lz4/lz4> (BSD 2-Clause) @ v1.9.4.
- **pugixml** sourced from <https://github.com/zeux/pugixml> (MIT) @ v1.14.

## Performance and Testing
Vendor payloads must remain under a compressed **5 MB** performance budget. After any vendor update, run `ctest` to confirm that integration tests continue to pass and measure startup time to stay within the budget.
