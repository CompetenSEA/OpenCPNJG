import base64
import os
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIST = ROOT.parent / 'server-styling' / 'dist'

# Minimal assets required for tileserver import
(DIST / 'sprites').mkdir(parents=True, exist_ok=True)
(DIST / 'assets' / 's52').mkdir(parents=True, exist_ok=True)
(DIST / 'style.s52.day.json').write_text('{"version":8,"sources":{},"layers":[]}')
(DIST / 'sprites' / 's52-day.json').write_text('{}')
(DIST / 'assets' / 's52' / 'rastersymbols-day.png').write_bytes(base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/woAAgMBgNwK9+wAAAAASUVORK5CYII="
))
(DIST / 'assets' / 's52' / 'chartsymbols.xml').write_text('<root><color-table name="DAY_BRIGHT"></color-table></root>')


def _make_mbtiles(path: Path, tile_bytes: bytes) -> None:
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)')
    conn.execute('CREATE TABLE metadata (name TEXT, value TEXT)')
    conn.execute('INSERT INTO metadata (name,value) VALUES ("format","pbf")')
    conn.executemany('INSERT INTO metadata (name,value) VALUES (?,?)',
                     [("bounds", "0,0,1,1"), ("minzoom", "0"), ("maxzoom", "5")])
    conn.execute('INSERT INTO tiles VALUES (0,0,0,?)', (tile_bytes,))
    conn.commit()
    conn.close()


@pytest.mark.skipif('tileserver' in sys.modules, reason='tileserver already loaded')
def test_mbtiles_stream(tmp_path, monkeypatch):
    mb = tmp_path / 'one.mbtiles'
    tile = b'xyz'
    _make_mbtiles(mb, tile)
    monkeypatch.setenv('ENC_DIR', str(tmp_path))
    import importlib.util
    import prometheus_client
    reg = prometheus_client.CollectorRegistry()
    prometheus_client.registry.REGISTRY = reg
    prometheus_client.metrics.REGISTRY = reg
    spec = importlib.util.spec_from_file_location('tileserver_mb', ROOT / 'tileserver.py')
    tileserver = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tileserver)
    client = TestClient(tileserver.app)
    r = client.get('/tiles/enc/0/0/0?fmt=mvt')
    assert r.status_code == 200
    assert r.content == tile
    assert r.headers['content-type'] == 'application/x-protobuf'
    assert 'ETag' in r.headers
    assert r.headers['Cache-Control'] == 'public, max-age=60'
    # add second dataset
    _make_mbtiles(tmp_path / 'two.mbtiles', tile)
    r2 = client.get('/tiles/enc/0/0/0?fmt=mvt')
    assert r2.status_code == 404
    r3 = client.get('/tiles/enc/one/0/0/0?fmt=mvt')
    assert r3.status_code == 200
    assert r3.content == tile
    r4 = client.get('/tiles/enc/one/0/0/0?fmt=png')
    assert r4.status_code == 415
    r5 = client.get('/tiles/enc/one/0/0/99?fmt=mvt')
    assert r5.status_code == 422
