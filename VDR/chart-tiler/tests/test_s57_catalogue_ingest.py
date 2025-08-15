from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ASSETS_CSV = ROOT.parent / "server-styling" / "dist" / "assets" / "s52" / "s57objectclasses.csv"

from s52_preclass import S52PreClassifier
from mvt_builder import encode_mvt


def test_s57_catalogue_ingest():
    if not ASSETS_CSV.exists():
        pytest.skip("s57objectclasses.csv not staged")
    classifier = S52PreClassifier(0.0, {})
    with ASSETS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            objl = row.get("Acronym") or row.get("acronym")
            if not objl:
                continue
            props = {"OBJL": objl}
            props.update(classifier.classify(objl, props))
            feat = {"geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, "properties": props}
            data = encode_mvt([feat])
            assert isinstance(data, (bytes, bytearray)) and data
