# Phase 6 – Assets, palettes and coverage wave 2

## Summary
- Enforce local asset flow and document hygiene rules.
- Generate day/dusk/night styles with helper and wave‑2 S‑52 layers.
- Track coverage deltas and surface them in docs and CI.

## Testing
- `pytest VDR/server-styling/tests -q`
- `pytest VDR/chart-tiler/tests -q`
- `python VDR/server-styling/tools/build_all_styles.py ...` (see docs)
- `python VDR/server-styling/s52_coverage.py --chartsymbols ...`

## Rollback
Revert the commits in `VDR/server-styling` and `VDR/docs` and rerun coverage.

