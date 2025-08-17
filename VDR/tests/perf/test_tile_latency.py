import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] / "chart-tiler"
sys.path.insert(0, str(ROOT))
DIST = ROOT.parent / "server-styling" / "dist"

# Ensure minimal styling assets exist for server import
(DIST / "sprites").mkdir(parents=True, exist_ok=True)
(DIST / "assets" / "s52").mkdir(parents=True, exist_ok=True)
(DIST / "sprites" / "s52-day.json").write_text("{}")
(DIST / "assets" / "s52" / "chartsymbols.xml").write_text(
    "<root><color-table name='DAY_BRIGHT'><color name='X' r='0' g='0' b='0'/></color-table></root>"
)

import tileserver  # noqa: E402

client = TestClient(tileserver.app)


def _p95(values: list[float]) -> float:
    values = sorted(values)
    idx = max(int(len(values) * 0.95) - 1, 0)
    return values[idx]


def _check(path: str, max_size: int) -> None:
    # warm cache
    client.get(path)
    durations: list[float] = []
    sizes: list[int] = []
    for _ in range(10):
        start = time.perf_counter()
        r = client.get(path)
        durations.append(time.perf_counter() - start)
        sizes.append(len(r.content))
    assert _p95(durations) * 1000 < 150
    assert max(sizes) < max_size


def test_tile_latency() -> None:
    _check("/tiles/cm93-core/8/0/0.pbf", 200 * 1024)
    _check("/tiles/cm93-core/12/0/0.pbf", 200 * 1024)
    _check("/tiles/cm93-core/13/0/0.pbf", 400 * 1024)
