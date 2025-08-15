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

client = TestClient(tileserver.app)


def _decode(sc: float):
    r = client.get(f"/tiles/cm93/0/0/0?fmt=mvt&sc={sc}")
    assert r.status_code == 200
    data = mapbox_vector_tile.decode(r.content)
    return data["features"]["features"]


def test_mvt_properties_present() -> None:
    feats = _decode(10)
    assert isinstance(feats, list)
    for feat in feats:
        assert isinstance(feat["properties"].get("OBJL"), str)


def test_depare_banding_sc_switch() -> None:
    f5 = _decode(5)
    f50 = _decode(50)
    toggled = False
    for a, b in zip(f5, f50):
        if a["properties"].get("OBJL") == "DEPARE" and b["properties"].get("OBJL") == "DEPARE":
            if a["properties"].get("isShallow") != b["properties"].get("isShallow"):
                toggled = True
                break
    assert toggled


def test_depcnt_safety_lowacc() -> None:
    feats = _decode(10)
    assert any(f["properties"].get("isSafety") for f in feats if f["properties"].get("OBJL") == "DEPCNT")
    assert any(f["properties"].get("isLowAcc") for f in feats if f["properties"].get("OBJL") == "DEPCNT")


def test_soundg_threshold() -> None:
    f5 = _decode(5)
    f50 = _decode(50)
    flipped = False
    for a, b in zip(f5, f50):
        if a["properties"].get("OBJL") == "SOUNDG" and b["properties"].get("OBJL") == "SOUNDG":
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
    feats = _decode(10)
    hazard_feats = [f for f in feats if f["properties"].get("OBJL") in ("WRECKS", "OBSTRN")]
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
    feats = _decode(10)
    hazard_feats = [f for f in feats if f["properties"].get("OBJL") in ("WRECKS", "OBSTRN")]
    sprite = json.loads((DIST / "sprites" / "s52-day.json").read_text())
    assert any(
        f["properties"].get("hazardIcon") and f"s52-{f['properties']['hazardIcon']}" in sprite
        for f in hazard_feats
    )


def test_hazard_offsets_present() -> None:
    feats = _decode(10)
    hazards = [f for f in feats if f["properties"].get("hazardIcon") == "DANGER51"]
    if not hazards:
        pytest.skip("DANGER51 feature missing")
    assert any(
        "hazardOffX" in h["properties"] and "hazardOffY" in h["properties"] for h in hazards
    )


def test_headers_and_cache() -> None:
    client.get("/tiles/cm93/0/0/0?fmt=mvt&sc=9")
    r2 = client.get("/tiles/cm93/0/0/0?fmt=mvt&sc=9")
    assert r2.headers.get("X-Tile-Cache") == "hit"
    metrics = client.get("/metrics").text
    m = re.search(r"cache_hits_total (\d+)", metrics)
    assert m and int(m.group(1)) >= 1
