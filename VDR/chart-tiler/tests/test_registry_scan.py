import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import sqlite3
from pathlib import Path

from registry import Registry


def make_mbtiles(path: Path, name="chart"):
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


def test_scan(tmp_path):
    mb = tmp_path / "a.mbtiles"
    make_mbtiles(mb, name="Sample")
    cog = tmp_path / "b.cog.tif"
    cog.write_bytes(b"cog")
    cog_json = tmp_path / "b.cog.json"
    cog_json.write_text(json.dumps({"bbox": [0, 0, 2, 2]}))
    r = Registry(tmp_path / "reg.sqlite")
    r.scan([tmp_path])
    # should include mbtiles, cog and osm
    all_items = r.list()
    kinds = {c.kind for c in all_items}
    assert {"enc", "geotiff", "osm"} <= kinds
    # filter by kind
    geos = r.list(kind="geotiff")
    assert geos and geos[0].id == "b"
    # search
    mbtiles = r.list(q="Sample")
    assert mbtiles and mbtiles[0].id == "a"
