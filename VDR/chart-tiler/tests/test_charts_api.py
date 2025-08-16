import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from fastapi.testclient import TestClient

from tileserver import app, reg


def test_charts_list_and_filter(tmp_path, monkeypatch):
    # prepare registry with fake records
    from registry import Registry
    r = Registry(tmp_path / "r.sqlite")
    r.scan([tmp_path])
    monkeypatch.setattr("tileserver.reg", r)
    client = TestClient(app)
    resp = client.get("/charts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # default includes osm
    assert any(d["id"] == "osm" for d in data)
    resp = client.get("/charts", params={"kind": "osm"})
    assert resp.json()[0]["id"] == "osm"
    # detail
    resp = client.get("/charts/osm")
    assert resp.status_code == 200
    assert resp.json()["id"] == "osm"
