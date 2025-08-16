from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from s52_preclass import S52PreClassifier, ContourConfig


def _contour(val: float) -> dict:
    return {
        "geometry": {"type": "LineString", "coordinates": [[0, 0], [0, 1 + val / 100]]},
        "properties": {"OBJL": "DEPCNT", "VALDCO": val},
    }


def _classify(vals: list[float], safety: float) -> list[dict]:
    cfg = ContourConfig(safety=safety)
    clf = S52PreClassifier(cfg, {})
    feats = []
    for v in vals:
        feat = _contour(v)
        feat["properties"].update(clf.classify("DEPCNT", feat["properties"]))
        feats.append(feat)
    mark = S52PreClassifier.finalize_tile(feats, cfg)
    for idx in mark:
        feats[idx]["properties"]["role"] = "safety"
    return feats


def test_finalize_promotes_deeper() -> None:
    feats = _classify([5, 15, 20], safety=10)
    roles = [f["properties"].get("role") for f in feats]
    assert roles[1] == "safety"
    assert roles.count("safety") == 1


def test_finalize_promotes_shallow_when_needed() -> None:
    feats = _classify([5, 15, 20], safety=22)
    roles = [f["properties"].get("role") for f in feats]
    assert roles[2] == "safety"
    assert roles.count("safety") == 1
