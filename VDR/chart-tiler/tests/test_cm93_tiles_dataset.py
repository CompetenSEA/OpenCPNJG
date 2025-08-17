import csv
import json
from pathlib import Path

from fastapi.testclient import TestClient

BASE = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(BASE))

from registry import get_registry
from cm93_importer import apply_offsets
import tileserver

FIX = Path(__file__).parent / "fixtures" / "cm93"


def test_cm93_tiles_and_offsets(tmp_path):
    reg = get_registry()
    ds = tmp_path / "testcm93.db"
    ds.write_text("stub")
    meta = tmp_path / "testcm93.cm93.json"
    meta.write_text(json.dumps({"bbox": [0, 0, 0, 0]}))
    reg.register_cm93(meta, ds)

    client = TestClient(tileserver.app)
    r = client.get("/tiles/cm93/testcm93/0/0/0.pbf")
    assert r.status_code == 200
    assert r.content

    features = json.loads((FIX / "cells.geojson").read_text())["features"]
    offsets = {}
    with (FIX / "offsets.csv").open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            offsets[row["cell_id"]] = (float(row["offset_dx_m"]), float(row["offset_dy_m"]))
    adjusted = apply_offsets(features, offsets)
    assert adjusted[0]["geometry"] != features[0]["geometry"]
