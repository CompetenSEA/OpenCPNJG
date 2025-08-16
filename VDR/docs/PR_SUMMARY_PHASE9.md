Summary

Portrayal Wave 2 significantly improves LIGHTS (labels, sectors), navaids sprites, depth formatting/contours, and UDW hazards while preserving presence=100% and S-57 handled ≥99%.

Coverage now reports by-type and by-bucket portrayal metrics; docs reflect the new lines.

Testing

Commands above. Node style-spec enables validator steps (skipped gracefully when absent).

Risks & Rollback

Conservative feature portrayal; fall back to stubs when assets/attributes are absent. Roll back by disabling sector/label features (leave --labels off) and reverting touched files.
