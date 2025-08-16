import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient

from tileserver import app, _geo_hits, reg
from registry import ChartRecord


def test_geotiff_tiles_cache(tmp_path, monkeypatch):
    dummy = tmp_path / "d.tif"
    dummy.write_bytes(b"0")
    rec = ChartRecord("test", "geotiff", "t", [0, 0, 1, 1], 0, 0, 0, path=str(dummy))
    monkeypatch.setattr(reg, "get", lambda cid: rec if cid == "test" else None)
    client = TestClient(app)
    r1 = client.get("/tiles/geotiff/test/0/0/0.png")
    assert r1.status_code == 200
    assert r1.headers["X-Tile-Cache"] == "miss"
    assert "Cache-Control" in r1.headers
    hits_before = _geo_hits._value.get() if hasattr(_geo_hits, "_value") else _geo_hits._value
    r2 = client.get("/tiles/geotiff/test/0/0/0.png")
    assert r2.headers["X-Tile-Cache"] == "hit"
    hits_after = _geo_hits._value.get() if hasattr(_geo_hits, "_value") else _geo_hits._value
    assert hits_after == hits_before + 1
