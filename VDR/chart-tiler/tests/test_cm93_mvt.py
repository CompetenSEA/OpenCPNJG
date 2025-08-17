import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import mapbox_vector_tile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import dict_builder
from tileserver import app


client = TestClient(app)


def _decode(content: bytes):
    return mapbox_vector_tile.decode(content)


def test_tile_endpoints_and_dict(tmp_path):
    dict_builder.build()  # create dictionary in default location
    # Dictionary endpoint
    resp = client.get("/tiles/cm93/dict.json")
    assert resp.status_code == 200
    mapping = json.loads(resp.text)
    assert "1" in mapping or 1 in mapping

    # Low zoom – soundings filtered by SCAMIN
    resp = client.get("/tiles/cm93-core/8/0/0.pbf")
    assert resp.status_code == 200
    assert len(resp.content) < 200 * 1024
    tile = _decode(resp.content)
    feats = tile["features"]["features"]
    objls = {f["properties"]["OBJL"] for f in feats}
    assert "SOUNDG" not in objls

    # High zoom – soundings visible
    resp = client.get("/tiles/cm93-core/12/0/0.pbf")
    assert resp.status_code == 200
    assert len(resp.content) < 400 * 1024
    tile = _decode(resp.content)
    feats = tile["features"]["features"]
    objls = {f["properties"]["OBJL"] for f in feats}
    assert "SOUNDG" in objls

    # Label plane reuses same data for now
    resp = client.get("/tiles/cm93-label/12/0/0.pbf")
    assert resp.status_code == 200
    assert len(resp.content) < 400 * 1024
