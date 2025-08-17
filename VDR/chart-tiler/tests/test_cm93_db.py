import json
import sqlite3
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "scripts"))

from cm93_importer import stream_to_db  # type: ignore
from validate_offsets import _load_offsets  # type: ignore

FIX = Path(__file__).parent / "fixtures" / "cm93"


def _conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE cm93_pts(cell_id INTEGER, geom TEXT)")
    c.execute("CREATE TABLE cm93_ln(cell_id INTEGER, geom TEXT)")
    c.execute("CREATE TABLE cm93_ar(cell_id INTEGER, geom TEXT)")
    c.execute("CREATE TABLE cm93_labels(cell_id INTEGER, text TEXT, geom TEXT)")
    c.execute("CREATE TABLE cm93_lights(cell_id INTEGER, geom TEXT, attrs TEXT)")
    c.execute(
        "CREATE TABLE cm93_cells(cell_id INTEGER PRIMARY KEY, bbox TEXT, offset_dx REAL, offset_dy REAL, meta_hash TEXT)"
    )
    return c


def _features():
    data = json.loads((FIX / "cells.geojson").read_text())
    return data["features"]


def test_stream_to_db_reimport():
    feats = _features()
    offsets = _load_offsets(FIX / "offsets.csv")
    conn = _conn()
    stream_to_db(feats, offsets, conn, bulk=True)
    # importing again should replace data rather than duplicate
    stream_to_db(feats, offsets, conn, bulk=True)
    cur = conn.execute("SELECT COUNT(*) FROM cm93_cells")
    assert cur.fetchone()[0] == 2
    cur = conn.execute("SELECT COUNT(*) FROM cm93_ar")
    assert cur.fetchone()[0] == 2
    cur = conn.execute("SELECT bbox, offset_dx FROM cm93_cells WHERE cell_id=1")
    bbox, dx = cur.fetchone()
    nums = list(map(float, bbox.split(",")))
    assert all(abs(a - b) < 1e-6 for a, b in zip(nums, [0.0, 0.0, 1.0, 1.0]))
    assert abs(dx + 1113.1576) < 1e-4
