import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "charts_py" / "src"))
from fastapi.testclient import TestClient
import tileserver

client = TestClient(tileserver.app)

def test_tile_endpoint_png():
    r = client.get("/tiles/0/0/0?fmt=png")
    assert r.status_code == 200
    assert r.content.startswith(b"\x89PNG")

def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"tile_gen_ms" in r.content
