# Performance Budgets

The tile server enforces lightweight performance gates during CI.

* **Latency:** 95th percentile response time for cached vector tiles must stay
  below **150&nbsp;ms**.
* **Payload size:** Vector tiles at zoom levels 0–12 must remain under
  **200&nbsp;KB**. Tiles at zoom **13 and above** may not exceed **400&nbsp;KB**.
* **Memory:** Resident set size of the tile server process should remain under
  **1 GiB**.

These thresholds are verified by `tests/perf/test_tile_latency.py`. Metrics are
exported via the `/metrics` endpoint using Prometheus format.

### Sample Prometheus Alerts

```yaml
- alert: TileLatencyHigh
  expr: histogram_quantile(0.95, sum(rate(tile_render_seconds_bucket[5m])) by (le,kind)) > 0.15
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High tile latency for {{ $labels.kind }}"
    description: "95th percentile tile latency exceeded 150ms for 10m"

- alert: TileSizeTooLarge
  expr: max_over_time(tile_size_bytes[5m]) > 400 * 1024
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Large tiles for {{ $labels.kind }}"
    description: "Vector tile size exceeded budget"

- alert: TileServerHighMemory
  expr: process_resident_memory_bytes > 1e9
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "Tile server memory high"
    description: "Resident memory usage over 1 GiB"
```
