from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "chart-tiler"
sys.path.insert(0, str(ROOT))

import mapbox_vector_tile
import pytest
from fastapi.testclient import TestClient
from datasource_stub import features_for_tile as _base_features
import tileserver  # noqa: E402

pytestmark = pytest.mark.tileserver

client = TestClient(tileserver.app)


def _decode_mvt(data: bytes):
    return mapbox_vector_tile.decode(data)


@pytest.fixture(autouse=True)
def _light_feature(monkeypatch):
    def _features(bbox, z, x, y):
        for f in _base_features(bbox, z, x, y):
            yield f
        minx, miny, maxx, maxy = bbox
        midx = (minx + maxx) / 2.0
        midy = (miny + maxy) / 2.0
        yield {
            "geometry": {"type": "Point", "coordinates": [midx, midy]},
            "properties": {"OBJL": "LIGHTS"},
        }

    monkeypatch.setattr(tileserver, "features_for_tile", _features)
    tileserver._render_mvt.cache_clear()


def test_cm93_core_tile_non_empty() -> None:
    resp = client.get("/tiles/cm93-core/14/0/0.pbf")
    assert resp.status_code == 200
    assert resp.content
    tile = _decode_mvt(resp.content)
    assert tile["features"]["features"]


def test_cm93_label_tile_non_empty() -> None:
    resp = client.get("/tiles/cm93-label/14/0/0.pbf")
    assert resp.status_code == 200
    assert resp.content
    tile = _decode_mvt(resp.content)
    assert tile["features"]["features"]
