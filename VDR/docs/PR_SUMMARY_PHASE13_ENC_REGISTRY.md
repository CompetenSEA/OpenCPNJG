**Summary**

* Introduced an ENC registry with `/charts` summary and per‑dataset routing `/tiles/enc/{ds}/...` plus a client picker that preserves mariner params.
* Extended MBTiles datasource summaries and caching with dataset‑aware headers.

**Testing**

* `pytest -q VDR/chart-tiler/tests/test_registry_scan.py`
* `pytest -q VDR/chart-tiler/tests/test_mbtiles_stream.py`
* `pytest -q VDR/chart-tiler/tests/test_metrics_idempotent.py`
* `npm test --prefix VDR/web-client`

**Risks & Rollback**

* Additive change; removing additional MBTiles reverts to single‑dataset mode.
* To rollback, serve a single dataset via `ENC_DIR` or pin `MBTILES_PATH`.
