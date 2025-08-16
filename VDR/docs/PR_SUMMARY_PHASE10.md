**Summary**

* End-to-end ingest: CM93→S-57 adapter (skip-safe), encode-time S-52 pre-classification, SCAMIN→minzoom mapping, and MBTiles streaming datasource. Names (OBJNAM/NOBJNM) render with zoom-scaled glyph labels when enabled.
* Presence=100% and S-57 handled ≥99% preserved; portrayal gates hold. Docs show by-type/by-bucket metrics.

**Testing**

* Commands above. CI enforces presence+catalogue gates and docs freshness; validator step runs when available.

**Risks & Rollback**

* Adapter path is isolated; fallback keeps previous stub behavior. Toggle `--respect-scamin` off to revert to tippecanoe defaults. Datasource falls back to deterministic stub when MBTiles not configured.
