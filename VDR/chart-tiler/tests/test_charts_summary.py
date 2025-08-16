import sqlite3
from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tileserver import app  # type: ignore


def _make_mbtiles(path: Path) -> None:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)')
    cur.execute('CREATE TABLE metadata (name TEXT, value TEXT)')
    cur.executemany('INSERT INTO metadata (name,value) VALUES (?,?)', [
        ('bounds', '0,0,1,1'),
        ('minzoom', '0'),
        ('maxzoom', '5'),
        ('name', 'A'),
    ])
    cur.execute('INSERT INTO tiles VALUES (0,0,0,?)', (b'x',))
    conn.commit()
    conn.close()


def test_charts_summary(tmp_path, monkeypatch):
    _make_mbtiles(tmp_path / 'a.mbtiles')
    monkeypatch.setenv('ENC_DIR', str(tmp_path))
    client = TestClient(app)
    resp = client.get('/charts')
    assert resp.status_code == 200
    data = resp.json()
    assert data['enc']['datasets'][0]['id'] == 'a'
