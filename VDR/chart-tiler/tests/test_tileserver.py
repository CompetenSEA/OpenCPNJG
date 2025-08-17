"""Integration tests for the lightweight tile server."""

from __future__ import annotations

import base64
import json
from pathlib import Path
import sys
import importlib

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIST = ROOT.parent / "server-styling" / "dist"

# Create minimal assets expected by the server ------------------------------
(DIST / "sprites").mkdir(parents=True, exist_ok=True)
(DIST / "assets" / "s52").mkdir(parents=True, exist_ok=True)

def _make_style(color: str) -> str:
    return json.dumps(
        {
            "version": 8,
            "sources": {},
            "layers": [
                {"id": "LNDARE", "type": "fill", "paint": {}},
                {"id": "DEPARE-shallow", "type": "fill", "paint": {}},
                {"id": "DEPARE-safe", "type": "fill", "paint": {}},
                {"id": "DEPCNT-base", "type": "line", "paint": {}},
                {"id": "DEPCNT-lowacc", "type": "line", "paint": {}},
                {"id": "DEPCNT-safety", "type": "line", "paint": {}},
                {"id": "COALNE", "type": "line", "paint": {}},
                {
                    "id": "SOUNDG",
                    "type": "symbol",
                    "layout": {},
                    "paint": {"text-color": color},
                },
            ],
        }
    )

(DIST / "style.s52.day.json").write_text(_make_style("#010203"))
(DIST / "style.s52.dusk.json").write_text(_make_style("#020202"))
(DIST / "style.s52.night.json").write_text(_make_style("#040506"))
(DIST / "sprites" / "s52-day.json").write_text("{}")
(DIST / "assets" / "s52" / "rastersymbols-day.png").write_bytes(
    base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/woAAgMBgNwK9+wAAAAASUVORK5CYII="
    )
)
# Minimal chartsymbols.xml for color parsing
(DIST / "assets" / "s52" / "chartsymbols.xml").write_text(
    "<root><color-table name='DAY_BRIGHT'><color name='DEPVS' r='1' g='2' b='3'/>"
    "<color name='DEPDW' r='4' g='5' b='6'/></color-table></root>"
)

import tileserver

client = TestClient(tileserver.app)


def test_tile_endpoint_png() -> None:
    r = client.get("/tiles/cm93/0/0/0.png?sc=10")
    assert r.status_code == 200
    assert r.content.startswith(b"\x89PNG")


def test_tile_endpoint_mvt() -> None:
    r = client.get("/tiles/cm93/0/0/0?fmt=mvt&sc=10")
    assert r.status_code == 200
    assert r.content  # Non-empty


def test_style_and_sprite_endpoints() -> None:
    assert client.get("/style/s52.day.json").status_code == 200
    assert client.get("/style/s52.dusk.json").status_code == 200
    assert client.get("/style/s52.night.json").status_code == 200
    assert client.get("/sprites/s52-day.json").status_code == 200
    assert client.get("/sprites/s52-day.png").status_code == 200


def test_style_structure() -> None:
    data = json.loads(client.get("/style/s52.day.json").text)
    layer_ids = [l["id"] for l in data["layers"]]
    expected = [
        "LNDARE",
        "DEPARE-shallow",
        "DEPARE-safe",
        "DEPCNT-base",
        "DEPCNT-lowacc",
        "DEPCNT-safety",
        "COALNE",
        "SOUNDG",
    ]
    for eid in expected:
        assert eid in layer_ids


def test_style_palettes_differ() -> None:
    day = json.loads(client.get("/style/s52.day.json").text)
    night = json.loads(client.get("/style/s52.night.json").text)
    day_col = next(lyr for lyr in day["layers"] if lyr["id"] == "SOUNDG")["paint"]["text-color"]
    night_col = next(lyr for lyr in night["layers"] if lyr["id"] == "SOUNDG")["paint"]["text-color"]
    assert day_col != night_col


def test_metrics_endpoint() -> None:
    # Trigger metric collection
    client.get("/tiles/cm93-core/0/0/0.pbf")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"tile_render_seconds" in r.content
    assert b"tile_bytes_total" in r.content


def test_metrics_endpoint_idempotent_import() -> None:
    # Ensure minimal color table exists for reload
    (DIST / "assets" / "s52" / "chartsymbols.xml").write_text(
        "<root><color-table name='DAY_BRIGHT'></color-table></root>"
    )
    mod = importlib.reload(tileserver)
    new_client = TestClient(mod.app)
    r = new_client.get("/metrics")
    assert r.status_code == 200
