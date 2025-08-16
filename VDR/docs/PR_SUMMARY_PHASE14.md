Summary

Implemented SCAMIN mapping (opt-in), MBTiles datasource with info endpoint, and a portrayal polish pass (Lights labels/sectors, Navaids rotation/names, Hazards with WATLEV variants, normalized line/pattern rendering) while preserving presence=100%.

Testing

Commands above. Optional validator is installed transiently and skipped gracefully if absent.

Risks & Rollback

All new behavior is behind flags or optional backends (--respect-scamin, MBTiles env). Disable flags or unset env to return to previous behavior.
