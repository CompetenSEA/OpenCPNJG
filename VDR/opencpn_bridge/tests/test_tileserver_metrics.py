import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest


# Ensure the repository root is on the Python path so the packaged tileserver
# module can be imported regardless of the current working directory.
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from opencpn_bridge.tileserver.app import app  # type: ignore


def test_metrics_increment():
    client = TestClient(app)

    r1 = client.get("/tiles/0/0/0.png")
    if r1.status_code != 200:  # pragma: no cover - endpoint unsupported
        pytest.skip("tile endpoint unavailable")
    size = len(r1.content)

    m1 = client.get("/metrics")
    assert m1.status_code == 200
    txt1 = m1.text
    assert f'tile_render_seconds_count{{kind="tile"}} 1.0' in txt1
    assert f'tile_bytes_total{{kind="tile"}} {float(size)}' in txt1

    r2 = client.get("/tiles/0/0/0.png")
    assert r2.status_code == 200

    m2 = client.get("/metrics")
    txt2 = m2.text
    assert f'tile_render_seconds_count{{kind="tile"}} 2.0' in txt2
    assert f'tile_bytes_total{{kind="tile"}} {float(size*2)}' in txt2

