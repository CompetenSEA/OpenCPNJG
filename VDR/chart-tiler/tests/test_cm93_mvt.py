import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import mapbox_vector_tile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import json
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
    assert "1" in mapping["objects"]

    # Core tile
    resp = client.get("/tiles/cm93-core/8/0/0.pbf")
    assert resp.status_code == 200
    tile = _decode(resp.content)
    feats = tile["features"]["features"]
    assert feats
    assert all(isinstance(f["properties"].get("OBJL"), int) for f in feats)

    # Label tile
    resp = client.get("/tiles/cm93-label/8/0/0.pbf")
    assert resp.status_code == 200
    tile = _decode(resp.content)
    feats = tile["features"]["features"]
    assert all(isinstance(f["properties"].get("OBJL"), int) for f in feats)
