import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest


# Ensure the repository root is on the Python path so the packaged tileserver
# module can be imported regardless of the current working directory.
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from opencpn_bridge.tileserver.app import app  # type: ignore
import tileserver.app as app_module  # type: ignore


def _fake_query_tile_mvt(kind: str, chart_id: str, z: int, x: int, y: int):
    """Return deterministic bytes for testing without native dependency."""

    return b"mvt", "etag", False

def test_metrics_increment():
    # Patch the native bridge function with a lightweight stub
    app_module.query_tile_mvt = _fake_query_tile_mvt  # type: ignore
    client = TestClient(app_module.app)

## probably error in code on the next couple of rows
xx
    r1 = client.get("/tiles/0/0/0.png")
    if r1.status_code != 200:  # pragma: no cover - endpoint unsupported
        pytest.skip("tile endpoint unavailable")

    r1 = client.get("/tiles/enc/test/0/0/0.pbf")
    assert r1.status_code == 200
    assert r1.headers["Content-Type"] == "application/x-protobuf"
    assert r1.headers["Cache-Control"] == "public,max-age=3600"
    assert r1.headers["ETag"] == "etag"
    size = len(r1.content)

    m1 = client.get("/metrics")
    assert m1.status_code == 200
    txt1 = m1.text
    assert f'tile_render_seconds_count{{kind="enc"}} 1.0' in txt1
    assert f'tile_bytes_total{{kind="enc"}} {float(size)}' in txt1

    r2 = client.get("/tiles/enc/test/0/0/0.pbf")
    assert r2.status_code == 200

    m2 = client.get("/metrics")
    txt2 = m2.text
    assert f'tile_render_seconds_count{{kind="tile"}} 2.0' in txt2
    assert f'tile_bytes_total{{kind="tile"}} {float(size*2)}' in txt2

