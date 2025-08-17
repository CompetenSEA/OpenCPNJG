import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIST = ROOT.parent / "server-styling" / "dist"

# Ensure minimal styling assets exist for server import
(DIST / "sprites").mkdir(parents=True, exist_ok=True)
(DIST / "assets" / "s52").mkdir(parents=True, exist_ok=True)
(DIST / "sprites" / "s52-day.json").write_text("{}")
(DIST / "assets" / "s52" / "chartsymbols.xml").write_text("<root/>")

import tileserver

client = TestClient(tileserver.app)


def _p90(values: list[float]) -> float:
    values = sorted(values)
    idx = max(int(len(values) * 0.9) - 1, 0)
    return values[idx]


def _check(path: str, max_size: int) -> None:
    # warm cache
    client.get(path)
    durations = []
    sizes = []
    for _ in range(10):
        start = time.perf_counter()
        r = client.get(path)
        durations.append(time.perf_counter() - start)
        sizes.append(len(r.content))
    assert _p90(durations) * 1000 < 150
    assert max(sizes) < max_size


def test_perf_tiles() -> None:
    _check("/tiles/cm93-core/8/0/0.pbf", 200 * 1024)
    _check("/tiles/cm93-core/12/0/0.pbf", 200 * 1024)
    _check("/tiles/cm93-core/15/0/0.pbf", 400 * 1024)
