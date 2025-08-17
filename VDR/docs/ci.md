# Continuous Integration

The VDR CI workflow is split into three jobs to build styling assets and run tests.

- **style-sprite** – prepares S-52 styling JSON and sprite sheets.  The job uses
  the repository Makefile to stage assets and publishes the `server-styling/dist`
  directory as a workflow artifact.
- **glyph-bake** – depends on Node.  It downloads the styling artifact, bakes
  font glyphs into PBF ranges and uploads the resulting `glyphs/` directory as
  an artifact.
- **tileserver-tests** – retrieves the styling and glyph artifacts and runs the
  chart tiler test-suite with `pytest` without accessing the network.
