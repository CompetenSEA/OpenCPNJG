import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sqlite3
from pathlib import Path

from registry import list_datasets


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
    make_mbtiles(tmp_path / "a.mbtiles", name="A")
    make_mbtiles(tmp_path / "b.mbtiles", name="B")
    datasets = list_datasets(tmp_path)
    ids = [d.id for d in datasets]
    assert ids == ["a", "b"]
    assert datasets[0].bounds == [0.0, 0.0, 1.0, 1.0]
    assert datasets[0].minzoom == 0 and datasets[0].maxzoom == 5
