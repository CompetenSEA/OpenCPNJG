import json
import sqlite3
from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tileserver  # type: ignore
from registry import Registry  # type: ignore


def make_mbtiles(path: Path, name: str):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE metadata (name TEXT, value TEXT)")
    cur.executemany(
        "INSERT INTO metadata VALUES (?,?)",
        [
            ("name", name),
            ("bounds", "0,0,1,1"),
            ("minzoom", "0"),
            ("maxzoom", "5"),
        ],
    )
    conn.commit()
    conn.close()


def setup_registry(tmp_path: Path):
    enc = tmp_path / "enc.mbtiles"
    make_mbtiles(enc, "enc")
    enc_meta = enc.with_suffix(".meta.json")
    enc_meta.write_text(
        json.dumps(
            {
                "kind": "enc",
                "name": "enc",
                "bounds": [0, 0, 1, 1],
                "minzoom": 0,
                "maxzoom": 5,
                "updatedAt": "2020-01-01T00:00:00",
                "cells": 1,
                "scamin": False,
                "sha256": "x",
            }
        )
    )
    cm = tmp_path / "cm.mbtiles"
    make_mbtiles(cm, "cm")
    cm_meta = cm.with_suffix(".meta.json")
    cm_meta.write_text(
        json.dumps(
            {
                "kind": "cm93",
                "name": "cm",
                "bounds": [0, 0, 1, 1],
                "minzoom": 0,
                "maxzoom": 5,
                "updatedAt": "2020-01-02T00:00:00",
                "cells": 1,
                "scamin": False,
                "sha256": "y",
            }
        )
    )
    cog = tmp_path / "geo.cog.tif"
    cog.write_bytes(b"cog")
    cog_json = cog.with_suffix(".json")
    cog_json.write_text(json.dumps({"bbox": [0, 0, 2, 2]}))
    reg = Registry(tmp_path / "reg.sqlite")
    reg.scan([tmp_path])
    tileserver.reg = reg
    tileserver._scan_registry = lambda: None
    client = TestClient(tileserver.app)
    return client


def test_registry_api_phase2(tmp_path: Path):
    client = setup_registry(tmp_path)
    resp = client.get("/charts")
    assert resp.status_code == 200
    kinds = {i["kind"] for i in resp.json()}
    assert {"enc", "cm93", "geotiff", "osm"} <= kinds
    resp = client.get("/charts", params={"kind": "enc"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    cid = resp.json()[0]["id"]
    detail = client.get(f"/charts/{cid}")
    assert detail.status_code == 200
    thumb = client.get(f"/charts/{cid}/thumbnail")
    assert thumb.status_code in (200, 404)
