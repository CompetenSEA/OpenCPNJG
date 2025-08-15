# Phase 5: palettes and contour config

## What changed
- Added generic palette parsing and `--palette` flag for style generation.
- Introduced typed `ContourConfig` used by classifier and tileserver with new query params.

## How to run
- Build styles for each palette using `--palette day|dusk|night`.
- Request tiles with `/tiles/...?...&safety=10&shallow=5&deep=30` or legacy `sc`.

## Risks & roll-back
- Tiles cached without thresholds may miss cache after upgrade; clear caches if needed.
- Older clients using only `sc` remain supported.
