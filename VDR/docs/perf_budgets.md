# Performance Budgets

The tile server enforces lightweight performance gates during CI.

* **Latency:** 90th percentile response time for cached vector tiles must be
  below **150&nbsp;ms**.
* **Payload size:** Vector tiles at zoom levels 0–12 must remain under
  **200&nbsp;KB**.  Tiles at zoom 13 and above may not exceed **400&nbsp;KB**.

These thresholds are verified by `test_perf_tiles.py`.  Alerting can be wired to
Prometheus by scraping the `/metrics` endpoint and firing alerts when
`tile_render_seconds` or `tile_bytes_total` exceed these limits for sustained
periods.
