import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from fastapi.testclient import TestClient

from tileserver import app, reg


def test_charts_list_and_filter(tmp_path, monkeypatch):
    # prepare registry with fake records
    from registry import Registry

    # create one GeoTIFF
    (tmp_path / "a.cog.tif").write_bytes(b"x")
    (tmp_path / "a.cog.json").write_text(json.dumps({"bbox": [0, 0, 1, 1]}))
    r = Registry(tmp_path / "r.sqlite")
    r.scan([tmp_path])
    monkeypatch.setattr("tileserver.reg", r)
    client = TestClient(app)
    resp = client.get("/charts", params={"pageSize": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    # default includes osm
    resp = client.get("/charts")
    assert any(d["id"] == "osm" for d in resp.json())
    resp = client.get("/charts", params={"kind": "osm"})
    assert resp.json()[0]["id"] == "osm"
    # add another chart then rescan
    data_dir = Path(__file__).resolve().parents[1] / "data"
    (data_dir / "b.cog.tif").write_bytes(b"x")
    (data_dir / "b.cog.json").write_text(json.dumps({"bbox": [0, 0, 1, 1]}))
    scan = client.post("/charts/scan")
    assert scan.json()["scanned"] is True
    resp = client.get("/charts", params={"kind": "geotiff"})
    ids = {d["id"] for d in resp.json()}
    assert {"a", "b"} <= ids
    # detail
    resp = client.get("/charts/osm")
    assert resp.status_code == 200
    assert resp.json()["id"] == "osm"
