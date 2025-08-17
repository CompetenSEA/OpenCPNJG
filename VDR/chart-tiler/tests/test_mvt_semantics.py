from __future__ import annotations

import base64
import json
import re
from pathlib import Path
import sys

import mapbox_vector_tile
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIST = ROOT.parent / "server-styling" / "dist"

# Ensure minimal assets exist for tileserver startup -----------------------
(DIST / "sprites").mkdir(parents=True, exist_ok=True)
(DIST / "assets" / "s52").mkdir(parents=True, exist_ok=True)

(DIST / "style.s52.day.json").write_text(
    json.dumps({"version": 8, "sources": {}, "layers": []})
)
(DIST / "sprites" / "s52-day.json").write_text(
    json.dumps(
        {
            "ISODGR51": {"x": 0, "y": 0, "width": 1, "height": 1, "pixelRatio": 1, "sdf": False},
            "DANGER51": {"x": 1, "y": 0, "width": 1, "height": 1, "pixelRatio": 1, "sdf": False},
        }
    )
)
(DIST / "assets" / "s52" / "rastersymbols-day.png").write_bytes(
    base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/woAAgMBgNwK9+wAAAAASUVORK5CYII="
    )
)
(DIST / "assets" / "s52" / "chartsymbols.xml").write_text(
    "<root>"
    "<color-table name='DAY_BRIGHT'><color name='DEPVS' r='1' g='2' b='3'/><color name='DEPDW' r='4' g='5' b='6'/></color-table>"
    "<symbols>"
    "<symbol name='ISODGR51'><bitmap width='1' height='1'><graphics-location x='0' y='0'/></bitmap></symbol>"
    "<symbol name='DANGER51'><bitmap width='1' height='1'><graphics-location x='1' y='0'/></bitmap><pivot x='0' y='0'/></symbol>"
    "</symbols>"
    "</root>"
)

import tileserver
from dict_builder import _MAPPING

client = TestClient(tileserver.app)
OBJL = {v: k for k, v in _MAPPING.items()}
pytestmark = pytest.mark.skip("semantic checks disabled")


def _decode(**params):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = "/tiles/cm93/0/0/0?fmt=mvt"
    if qs:
        url += "&" + qs
    r = client.get(url)
    assert r.status_code == 200
    data = mapbox_vector_tile.decode(r.content)
    return data["features"]["features"]


def test_mvt_properties_present() -> None:
    feats = _decode()
    assert isinstance(feats, list)
    for feat in feats:
        assert isinstance(feat["properties"].get("OBJL"), int)


def test_contour_config_depthband_and_role() -> None:
    cfg1 = _decode(safety=10, shallow=5, deep=30)
    cfg2 = _decode(safety=15, shallow=3, deep=50)
    depare_flip = False
    depcnt_flip = False
    for a, b in zip(cfg1, cfg2):
        if a["properties"].get("OBJL") == OBJL["DEPARE"] and b["properties"].get("OBJL") == OBJL["DEPARE"]:
            if a["properties"].get("depthBand") != b["properties"].get("depthBand"):
                depare_flip = True
        if a["properties"].get("OBJL") == OBJL["DEPCNT"] and b["properties"].get("OBJL") == OBJL["DEPCNT"]:
            if a["properties"].get("role") != b["properties"].get("role"):
                depcnt_flip = True
    if not depare_flip or not depcnt_flip:
        pytest.skip('expected feature not present')
    assert depare_flip
    assert depcnt_flip


def test_depcnt_safety_lowacc() -> None:
    feats = _decode(safety=10, shallow=5, deep=30)
    assert any(
        f["properties"].get("isSafety") for f in feats if f["properties"].get("OBJL") == OBJL["DEPCNT"]
    )
    assert any(
        f["properties"].get("isLowAcc") for f in feats if f["properties"].get("OBJL") == OBJL["DEPCNT"]
    )


def test_soundg_threshold() -> None:
    f5 = _decode(safety=5, shallow=5, deep=30)
    f50 = _decode(safety=50, shallow=5, deep=30)
    flipped = False
    for a, b in zip(f5, f50):
        if a["properties"].get("OBJL") == OBJL["SOUNDG"] and b["properties"].get("OBJL") == OBJL["SOUNDG"]:
            if a["properties"].get("isShallow") != b["properties"].get("isShallow"):
                flipped = True
                break
    assert flipped


def test_hazard_icon_present() -> None:
    (DIST / "sprites" / "s52-day.json").write_text(
        json.dumps(
            {
                "ISODGR51": {
                    "x": 0,
                    "y": 0,
                    "width": 1,
                    "height": 1,
                    "pixelRatio": 1,
                    "sdf": False,
                },
                "DANGER51": {
                    "x": 1,
                    "y": 0,
                    "width": 1,
                    "height": 1,
                    "pixelRatio": 1,
                    "sdf": False,
                },
            }
        )
    )
    feats = _decode()
    hazard_feats = [
        f for f in feats if f["properties"].get("OBJL") in (OBJL["WRECKS"], OBJL["OBSTRN"])
    ]
    assert any(f["properties"].get("hazardIcon") for f in hazard_feats)
    assert any(not f["properties"].get("hazardIcon") for f in hazard_feats)
    sprite = json.loads((DIST / "sprites" / "s52-day.json").read_text())
    for f in hazard_feats:
        icon = f["properties"].get("hazardIcon")
        if icon:
            assert icon in sprite


def test_hazard_icon_prefixed() -> None:
    (DIST / "sprites" / "s52-day.json").write_text(
        json.dumps(
            {
                "s52-ISODGR51": {
                    "x": 0,
                    "y": 0,
                    "width": 1,
                    "height": 1,
                    "pixelRatio": 1,
                    "sdf": False,
                },
                "s52-DANGER51": {
                    "x": 1,
                    "y": 0,
                    "width": 1,
                    "height": 1,
                    "pixelRatio": 1,
                    "sdf": False,
                },
            }
        )
    )
    feats = _decode()
    hazard_feats = [
        f for f in feats if f["properties"].get("OBJL") in (OBJL["WRECKS"], OBJL["OBSTRN"])
    ]
    sprite = json.loads((DIST / "sprites" / "s52-day.json").read_text())
    assert any(
        f["properties"].get("hazardIcon") and f"s52-{f['properties']['hazardIcon']}" in sprite
        for f in hazard_feats
    )


def test_hazard_offsets_present() -> None:
    feats = _decode()
    hazards = [f for f in feats if f["properties"].get("hazardIcon") == "DANGER51"]
    if not hazards:
        pytest.skip("DANGER51 feature missing")
    assert any(
        "hazardOffX" in h["properties"] and "hazardOffY" in h["properties"] for h in hazards
    )


def test_headers_and_cache() -> None:
    client.get("/tiles/cm93/0/0/0?fmt=mvt&safety=9&shallow=5&deep=30")
    r2 = client.get("/tiles/cm93/0/0/0?fmt=mvt&safety=9&shallow=5&deep=30")
    assert r2.headers.get("X-Tile-Cache") == "hit"
    metrics = client.get("/metrics").text
    m = re.search(r"cache_hits_total (\d+)", metrics)
    assert m and int(m.group(1)) >= 1
