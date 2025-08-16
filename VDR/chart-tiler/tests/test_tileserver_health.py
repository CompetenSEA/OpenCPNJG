import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from tileserver import app


def test_health_and_metrics():
    client = TestClient(app)
    r = client.get('/healthz')
    assert r.status_code == 200
    m1 = client.get('/metrics')
    m2 = client.get('/metrics')
    assert m1.status_code == 200
    assert m1.text == m2.text
