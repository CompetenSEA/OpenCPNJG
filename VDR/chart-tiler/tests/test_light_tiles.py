import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
import mapbox_vector_tile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import tileserver
from lights import build_light_character
from datasource_stub import features_for_tile as _base_features
from dict_builder import _MAPPING

client = TestClient(tileserver.app)
OBJL = {v: k for k, v in _MAPPING.items()}

LIGHT_ATTRS = {
    "LITCHR": "Fl",
    "SIGGRP": "(3)",
    "COLOUR": "red",
    "SIGPER": "5s",
    "VALNMR": 0.05,
    "SECTR1": 0,
    "SECTR2": 90,
}


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
            "properties": {"OBJL": "LIGHTS", **LIGHT_ATTRS},
        }
    monkeypatch.setattr(tileserver, "features_for_tile", _features)
    tileserver._render_mvt.cache_clear()


def _decode(content: bytes):
    return mapbox_vector_tile.decode(content)


def test_core_contains_sector_geometry():
    resp = client.get("/tiles/cm93-core/14/0/0.pbf")
    assert resp.status_code == 200
    tile = _decode(resp.content)
    feats = tile["features"]["features"]
    lights = [f for f in feats if f["properties"].get("OBJL") == OBJL["LIGHTS"]]
    assert lights


def test_label_carries_character_code():
    resp = client.get("/tiles/cm93-label/14/0/0.pbf")
    assert resp.status_code == 200
    tile = _decode(resp.content)
    feats = tile["features"]["features"]
    code = build_light_character(LIGHT_ATTRS)
    assert any(
        f["properties"].get("text") == code and f["properties"].get("OBJL") == OBJL["LIGHTS"]
        for f in feats
    )
