import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "scripts"))

from cm93_importer import apply_offsets
from validate_offsets import _load_offsets, validate

FIX = Path(__file__).parent / "fixtures" / "cm93"


def load_features():
    data = json.loads((FIX / "cells.geojson").read_text())
    return data["features"]


def test_apply_offsets():
    feats = load_features()
    offsets = _load_offsets(FIX / "offsets.csv")
    adj = apply_offsets(feats, offsets)
    # first feature should shift left by ~0.01 degrees (1113.2 m at equator)
    x0 = adj[0]["geometry"]["coordinates"][0][0][0]
    assert abs(x0 - 0.0) < 1e-6


def test_apply_offsets_high_lat():
    feats = [
        {
            "type": "Feature",
            "properties": {"cell_id": 9},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 59.5], [0, 60.5], [1, 60.5], [1, 59.5], [0, 59.5]]],
            },
        }
    ]
    offsets = {"9": (1113.2, 0.0)}
    adj = apply_offsets(feats, offsets)
    x0 = adj[0]["geometry"]["coordinates"][0][0][0]
    # At latitude 60°, 1113.2 m ≈ 0.02°
    assert abs(x0 - 0.02) < 1e-6


def test_validate_offsets():
    feats = load_features()
    offsets = _load_offsets(FIX / "offsets.csv")
    assert validate(feats, offsets, tolerance=0.02)
