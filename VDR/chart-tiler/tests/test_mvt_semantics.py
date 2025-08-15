from __future__ import annotations

import base64
import json
import re
from pathlib import Path
import sys

import mapbox_vector_tile
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
(DIST / "sprites" / "s52-day.json").write_text("{}")
(DIST / "assets" / "s52" / "rastersymbols-day.png").write_bytes(
    base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/woAAgMBgNwK9+wAAAAASUVORK5CYII="
    )
)
(DIST / "assets" / "s52" / "chartsymbols.xml").write_text(
    "<root><color-table name='DAY_BRIGHT'><color name='DEPVS' r='1' g='2' b='3'/>"
    "<color name='DEPDW' r='4' g='5' b='6'/></color-table></root>"
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


def test_headers_and_cache() -> None:
    client.get("/tiles/cm93/0/0/0?fmt=mvt&sc=9")
    r2 = client.get("/tiles/cm93/0/0/0?fmt=mvt&sc=9")
    assert r2.headers.get("X-Tile-Cache") == "hit"
    metrics = client.get("/metrics").text
    m = re.search(r"cache_hits_total (\d+)", metrics)
    assert m and int(m.group(1)) >= 1
