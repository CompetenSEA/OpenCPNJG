Summary

Automated S‑52 layer synthesis via --auto-cover (symbols/lines/areas/stubs), prefix‑safe sprites with anchor/rotation metadata; rich per‑layer tokens aid coverage.

Coverage pipeline now computes presence (target 100%) and portrayal metrics, writing separate reports. Docs show both percentages and gap lists.

CI stages local assets, builds three palettes with templated names, validates styles, enforces presence coverage, and refreshes docs.

Testing

Commands above. Install the Node style‑spec to enable validator steps.

Risks & Rollback

Tooling‑only changes with conservative fallbacks. Roll back by removing --auto-cover path and coverage enforcement, revert the touched files, and keep existing Tier‑1/Tier‑2 behavior.
