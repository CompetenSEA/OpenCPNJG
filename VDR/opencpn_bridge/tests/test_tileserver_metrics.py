import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tileserver.app import app  # type: ignore


def test_metrics_increment():
    client = TestClient(app)

    r1 = client.get("/tiles/0/0/0.png")
    assert r1.status_code == 200
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
